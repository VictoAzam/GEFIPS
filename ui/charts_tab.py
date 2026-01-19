from __future__ import annotations

from datetime import date
from typing import Any, Dict, List

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt5.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from database.db_manager import DbManager
from utils.formatters import format_brl


_PRIMARY = "#2E86AB"
_SECONDARY = "#18A999"
_DANGER = "#DC2626"
_MUTED = "#6B7280"


_MONTHS_SHORT = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"]


class ChartsTab(QWidget):
	def __init__(self, db: DbManager):
		super().__init__()
		self.db = db

		self.title = QLabel("Gráficos do mês")
		self.title.setObjectName("SectionTitle")

		self.fig_bar = Figure(figsize=(4.5, 3.0), dpi=100)
		self.canvas_bar = FigureCanvas(self.fig_bar)

		self.fig_pie = Figure(figsize=(4.5, 3.0), dpi=100)
		self.canvas_pie = FigureCanvas(self.fig_pie)

		row = QHBoxLayout()
		row.addWidget(self._card("Entradas x Saídas", self.canvas_bar), stretch=1)
		row.addWidget(self._card("Saídas por categoria", self.canvas_pie), stretch=1)

		root = QVBoxLayout()
		root.addWidget(self.title)
		root.addLayout(row)
		root.addStretch(1)
		self.setLayout(root)

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

	def refresh(self, year: int, month: int) -> None:
		m = _MONTHS_SHORT[month - 1]
		self.title.setText(f"Gráficos do mês: {m}/{year}")

		entradas, saidas, saldo = self.db.get_month_balance(year, month)
		self._plot_bar(entradas=entradas, saidas=saidas, saldo=saldo)

		rows = self.db.get_month_category_totals(year, month, tipo="saida")
		self._plot_pie(rows)

	def _plot_bar(self, entradas: float, saidas: float, saldo: float) -> None:
		self.fig_bar.clear()
		ax = self.fig_bar.add_subplot(111)

		labels = ["Entradas", "Saídas"]
		values = [float(entradas), float(saidas)]
		colors = [_SECONDARY, _DANGER]
		bars = ax.bar(labels, values, color=colors)

		ax.set_ylabel("R$")
		ax.tick_params(axis="x", labelrotation=0)
		ax.grid(axis="y", alpha=0.2)

		for bar, v in zip(bars, values):
			ax.text(
				bar.get_x() + bar.get_width() / 2,
				bar.get_height(),
				format_brl(v),
				ha="center",
				va="bottom",
				fontsize=9,
				color=_MUTED,
			)

		title = f"Saldo: {format_brl(saldo)}"
		ax.set_title(title, color=_PRIMARY)

		self.fig_bar.tight_layout()
		self.canvas_bar.draw()

	def _plot_pie(self, rows: List[Dict[str, Any]]) -> None:
		self.fig_pie.clear()
		ax = self.fig_pie.add_subplot(111)

		if not rows:
			ax.text(0.5, 0.5, "Sem dados no mês", ha="center", va="center", color=_MUTED)
			ax.set_axis_off()
			self.canvas_pie.draw()
			return

		labels = [str(r.get("categoria") or "(sem categoria)") for r in rows]
		values = [float(r.get("total") or 0.0) for r in rows]

		# Limita para manter legível
		max_slices = 8
		if len(values) > max_slices:
			top_labels = labels[:max_slices]
			top_values = values[:max_slices]
			others = sum(values[max_slices:])
			if others > 0:
				top_labels.append("Outros")
				top_values.append(others)
			labels, values = top_labels, top_values

		ax.pie(values, labels=labels, autopct="%1.0f%%", textprops={"fontsize": 9, "color": _MUTED})
		ax.axis("equal")

		self.fig_pie.tight_layout()
		self.canvas_pie.draw()
