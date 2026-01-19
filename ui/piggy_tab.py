from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Any, Dict, List, Optional

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
	QFrame,
	QHBoxLayout,
	QLabel,
	QMessageBox,
	QPushButton,
	QSpinBox,
	QStyle,
	QTableWidget,
	QTableWidgetItem,
	QVBoxLayout,
	QWidget,
)

from database.db_manager import DbManager
from database.models_investments import PiggyBank
from ui.dialogs.piggy_bank import PiggyBankDialog
from ui.icons import icon_add, icon_edit, icon_delete, icon_save, make_icon
from ui.theme import is_dark_mode
from utils.formatters import format_brl
from utils.investments import annual_rate_from_cdi, project_piggy
from utils.reports_piggy import generate_piggy_projection_report_pdf


_MONTHS_SHORT = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"]


class PiggyTab(QWidget):
	def __init__(self, db: DbManager, exports_dir: Path):
		super().__init__()
		self.db = db
		self.exports_dir = exports_dir
		style = self.style()

		color = "#F1F5F9" if is_dark_mode() else "#111827"
		self.btn_add = QPushButton("Adicionar cofrinho")
		self.btn_add.setIcon(make_icon(icon_add(), 20, color))
		self.btn_add.clicked.connect(self.add_piggy)

		self.btn_edit = QPushButton("Editar")
		self.btn_edit.setIcon(make_icon(icon_edit(), 20, color))
		self.btn_edit.clicked.connect(self.edit_selected)

		self.btn_delete = QPushButton("Excluir")
		self.btn_delete.setIcon(make_icon(icon_delete(), 20, color))
		self.btn_delete.clicked.connect(self.delete_selected)

		self.horizon = QSpinBox()
		self.horizon.setRange(1, 120)
		self.horizon.setValue(12)
		self.horizon.valueChanged.connect(lambda _v: self.refresh_projection())

		self.btn_report = QPushButton("Gerar relatório")
		self.btn_report.setIcon(make_icon(icon_save(), 20, color))
		self.btn_report.clicked.connect(self.generate_report)

		controls = QHBoxLayout()
		controls.addWidget(self.btn_add)
		controls.addWidget(self.btn_edit)
		controls.addWidget(self.btn_delete)
		controls.addSpacing(10)
		controls.addWidget(QLabel("Projeção (meses):"))
		controls.addWidget(self.horizon)
		controls.addWidget(self.btn_report)
		controls.addStretch(1)

		self.table = QTableWidget(0, 6)
		self.table.setHorizontalHeaderLabels(["Nome", "Instituição", "%CDI", "CDI a.a.", "Inicial", "Aporte/mês"])
		self.table.setSelectionBehavior(QTableWidget.SelectRows)
		self.table.setSelectionMode(QTableWidget.SingleSelection)
		self.table.setEditTriggers(QTableWidget.NoEditTriggers)
		self.table.itemSelectionChanged.connect(self.refresh_projection)

		self.proj_table = QTableWidget(0, 6)
		self.proj_table.setHorizontalHeaderLabels(["Mês", "Aportes", "Bruto", "Rend.", "Impostos", "Líquido"])
		self.proj_table.setSelectionBehavior(QTableWidget.SelectRows)
		self.proj_table.setEditTriggers(QTableWidget.NoEditTriggers)

		self.fig = Figure(figsize=(6.0, 2.6), dpi=100)
		self.canvas = FigureCanvas(self.fig)

		right = QVBoxLayout()
		label = QLabel("Projeção")
		label.setObjectName("SectionTitle")
		right.addWidget(label)
		right.addWidget(self._card("Evolução (bruto x líquido)", self.canvas))
		right.addWidget(self.proj_table)

		left = QVBoxLayout()
		label2 = QLabel("Cofrinhos")
		label2.setObjectName("SectionTitle")
		left.addWidget(label2)
		left.addWidget(self.table)

		row = QHBoxLayout()
		row.addLayout(left, stretch=1)
		row.addLayout(right, stretch=2)

		root = QVBoxLayout()
		root.addLayout(controls)
		root.addLayout(row)
		self.setLayout(root)

		self.refresh()

	def _card(self, title: str, widget: QWidget) -> QFrame:
		card = QFrame()
		card.setObjectName("Card")
		t = QLabel(title)
		t.setObjectName("CardTitle")
		layout = QVBoxLayout(card)
		layout.setContentsMargins(14, 12, 14, 12)
		layout.setSpacing(10)
		layout.addWidget(t)
		layout.addWidget(widget)
		return card

	def refresh(self) -> None:
		rows = self.db.list_piggy_banks()
		self.table.setRowCount(len(rows))	
		for r, row in enumerate(rows):
			pid = int(row.get("id") or 0)
			items = [
				QTableWidgetItem(str(row.get("nome") or "")),
				QTableWidgetItem(str(row.get("instituicao") or "")),
				QTableWidgetItem(f"{float(row.get('percent_cdi') or 0.0):.2f}%"),
				QTableWidgetItem(f"{float(row.get('cdi_aa') or 0.0):.2f}%"),
				QTableWidgetItem(format_brl(float(row.get("principal") or 0.0))),
				QTableWidgetItem(format_brl(float(row.get("aporte_mensal") or 0.0))),
			]
			items[0].setData(Qt.UserRole, pid)
			for c, it in enumerate(items):
				if c in (4, 5):
					it.setTextAlignment(int(Qt.AlignRight | Qt.AlignVCenter))
				self.table.setItem(r, c, it)

		self.refresh_projection()

	def _selected_id(self) -> Optional[int]:
		row = self.table.currentRow()
		if row < 0:
			return None
		it = self.table.item(row, 0)
		if not it:
			return None
		val = it.data(Qt.UserRole)
		try:
			return int(val)
		except Exception:
			return None

	def add_piggy(self) -> None:
		dlg = PiggyBankDialog(self)
		if dlg.exec_() != dlg.Accepted:
			return
		p = dlg.piggy
		if p is None:
			return
		self.db.add_piggy_bank(p)
		self.refresh()

	def edit_selected(self) -> None:
		pid = self._selected_id()
		if pid is None:
			QMessageBox.information(self, "Editar", "Selecione um cofrinho.")
			return
		row = self.db.get_piggy_bank(pid)
		if not row:
			QMessageBox.warning(self, "Editar", "Cofrinho não encontrado.")
			return
		d0 = date.fromisoformat(str(row.get("data_inicio")))
		initial = PiggyBank(
			id=pid,
			nome=str(row.get("nome")),
			instituicao=str(row.get("instituicao")),
			percent_cdi=float(row.get("percent_cdi") or 0.0),
			cdi_aa=float(row.get("cdi_aa") or 0.0),
			principal=float(row.get("principal") or 0.0),
			aporte_mensal=float(row.get("aporte_mensal") or 0.0),
			data_inicio=d0,
			aplicar_impostos=bool(row.get("aplicar_impostos")),
		)
		dlg = PiggyBankDialog(self, initial=initial)
		if dlg.exec_() != dlg.Accepted:
			return
		p = dlg.piggy
		if p is None:
			return
		self.db.update_piggy_bank(pid, p)
		self.refresh()

	def delete_selected(self) -> None:
		pid = self._selected_id()
		if pid is None:
			QMessageBox.information(self, "Excluir", "Selecione um cofrinho.")
			return
		resp = QMessageBox.question(
			self,
			"Excluir",
			"Tem certeza que deseja excluir o cofrinho selecionado?",
			QMessageBox.Yes | QMessageBox.No,
			QMessageBox.No,
		)
		if resp != QMessageBox.Yes:
			return
		self.db.delete_piggy_bank(pid)
		self.refresh()

	def refresh_projection(self) -> None:
		pid = self._selected_id()
		if pid is None:
			self._clear_projection()
			return
		row = self.db.get_piggy_bank(pid)
		if not row:
			self._clear_projection()
			return

		d0 = date.fromisoformat(str(row.get("data_inicio")))
		annual = annual_rate_from_cdi(float(row.get("cdi_aa") or 0.0), float(row.get("percent_cdi") or 0.0))
		points = project_piggy(
			start=d0,
			principal=float(row.get("principal") or 0.0),
			aporte_mensal=float(row.get("aporte_mensal") or 0.0),
			annual_rate=annual,
			horizon_months=int(self.horizon.value()),
			aplicar_impostos=bool(row.get("aplicar_impostos")),
		)

		self._render_projection(points)

	def _clear_projection(self) -> None:
		self.proj_table.setRowCount(0)
		self.fig.clear()
		self.canvas.draw()

	def _render_projection(self, points):
		self.proj_table.setRowCount(len(points))
		gross_series = []
		net_series = []
		labels = []
		for i, p in enumerate(points):
			labels.append(f"{_MONTHS_SHORT[p.ref_date.month-1]}/{str(p.ref_date.year)[-2:]}")
			gross_series.append(p.saldo_bruto)
			net_series.append(p.saldo_liquido)
			impostos = p.iof + p.ir

			items = [
				QTableWidgetItem(f"{_MONTHS_SHORT[p.ref_date.month-1]}/{p.ref_date.year}"),
				QTableWidgetItem(format_brl(p.total_aportes)),
				QTableWidgetItem(format_brl(p.saldo_bruto)),
				QTableWidgetItem(format_brl(p.rendimento_bruto)),
				QTableWidgetItem(format_brl(impostos)),
				QTableWidgetItem(format_brl(p.saldo_liquido)),
			]
			for c, it in enumerate(items):
				if c >= 1:
					it.setTextAlignment(int(Qt.AlignRight | Qt.AlignVCenter))
				self.proj_table.setItem(i, c, it)

		self.fig.clear()
		ax = self.fig.add_subplot(111)
		ax.plot(gross_series, label="Bruto")
		ax.plot(net_series, label="Líquido")
		step = max(1, len(labels) // 6)
		ticks = list(range(0, len(labels), step))
		ax.set_xticks(ticks)
		ax.set_xticklabels([labels[j] for j in ticks], rotation=0, fontsize=8)
		ax.grid(alpha=0.2)
		ax.legend(loc="upper left", fontsize=8)
		self.fig.tight_layout()
		self.canvas.draw()

	def generate_report(self) -> None:
		pid = self._selected_id()
		if pid is None:
			QMessageBox.information(self, "Relatório", "Selecione um cofrinho.")
			return
		row = self.db.get_piggy_bank(pid)
		if not row:
			QMessageBox.warning(self, "Relatório", "Cofrinho não encontrado.")
			return
		try:
			out = generate_piggy_projection_report_pdf(
				db=self.db,
				exports_dir=self.exports_dir,
				piggy_id=pid,
				horizon_months=int(self.horizon.value()),
			)
		except Exception as e:
			QMessageBox.critical(self, "Relatório", f"Falha ao gerar relatório: {e}")
			return
		QMessageBox.information(self, "Relatório", f"Relatório gerado em:\n{out}")
