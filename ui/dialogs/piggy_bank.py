from __future__ import annotations

from datetime import date
from typing import Optional

from PyQt5.QtCore import QDate
from PyQt5.QtWidgets import (
	QCheckBox,
	QComboBox,
	QDateEdit,
	QDialog,
	QDialogButtonBox,
	QDoubleSpinBox,
	QFormLayout,
	QLineEdit,
	QMessageBox,
	QVBoxLayout,
)

from database.models_investments import PiggyBank
from utils.validators import require_non_empty


class PiggyBankDialog(QDialog):
	def __init__(self, parent=None, initial: Optional[PiggyBank] = None):
		super().__init__(parent)
		self.setModal(True)
		self.setWindowTitle("Editar Cofrinho" if initial else "Adicionar Cofrinho")

		self._piggy: Optional[PiggyBank] = None

		self.nome = QLineEdit()
		self.instituicao = QLineEdit()
		self.percent_cdi = QDoubleSpinBox()
		self.percent_cdi.setDecimals(2)
		self.percent_cdi.setRange(0.0, 300.0)
		self.percent_cdi.setValue(100.0)
		self.percent_cdi.setSuffix("%")

		self.cdi_aa = QDoubleSpinBox()
		self.cdi_aa.setDecimals(2)
		self.cdi_aa.setRange(0.0, 50.0)
		self.cdi_aa.setValue(10.0)
		self.cdi_aa.setSuffix("% a.a.")

		self.principal = QDoubleSpinBox()
		self.principal.setDecimals(2)
		self.principal.setRange(0.0, 1_000_000_000.0)
		self.principal.setSingleStep(100.0)

		self.aporte_mensal = QDoubleSpinBox()
		self.aporte_mensal.setDecimals(2)
		self.aporte_mensal.setRange(0.0, 1_000_000_000.0)
		self.aporte_mensal.setSingleStep(50.0)

		self.data_inicio = QDateEdit()
		self.data_inicio.setCalendarPopup(True)
		self.data_inicio.setDate(QDate.currentDate())

		self.aplicar_impostos = QCheckBox("Aplicar IR/IOF (aproximação)")
		self.aplicar_impostos.setChecked(False)

		form = QFormLayout()
		form.addRow("Nome:", self.nome)
		form.addRow("Instituição:", self.instituicao)
		form.addRow("% do CDI:", self.percent_cdi)
		form.addRow("CDI atual:", self.cdi_aa)
		form.addRow("Valor inicial (R$):", self.principal)
		form.addRow("Aporte mensal (R$):", self.aporte_mensal)
		form.addRow("Data inicial:", self.data_inicio)
		form.addRow("", self.aplicar_impostos)

		btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
		btns.accepted.connect(self.accept)
		btns.rejected.connect(self.reject)

		root = QVBoxLayout()
		root.addLayout(form)
		root.addWidget(btns)
		self.setLayout(root)

		if initial:
			self._populate(initial)

	def _populate(self, p: PiggyBank) -> None:
		self.nome.setText(p.nome)
		self.instituicao.setText(p.instituicao)
		self.percent_cdi.setValue(float(p.percent_cdi))
		self.cdi_aa.setValue(float(p.cdi_aa))
		self.principal.setValue(float(p.principal))
		self.aporte_mensal.setValue(float(p.aporte_mensal))
		self.data_inicio.setDate(QDate(p.data_inicio.year, p.data_inicio.month, p.data_inicio.day))
		self.aplicar_impostos.setChecked(bool(p.aplicar_impostos))

	@property
	def piggy(self) -> Optional[PiggyBank]:
		return self._piggy

	def accept(self) -> None:
		try:
			nome = require_non_empty(self.nome.text(), "Nome")
			instituicao = require_non_empty(self.instituicao.text(), "Instituição")
			qd = self.data_inicio.date()
			d = date(qd.year(), qd.month(), qd.day())
			self._piggy = PiggyBank(
				id=None,
				nome=nome,
				instituicao=instituicao,
				percent_cdi=float(self.percent_cdi.value()),
				cdi_aa=float(self.cdi_aa.value()),
				principal=float(self.principal.value()),
				aporte_mensal=float(self.aporte_mensal.value()),
				data_inicio=d,
				aplicar_impostos=bool(self.aplicar_impostos.isChecked()),
			)
		except ValueError as e:
			QMessageBox.warning(self, "Validação", str(e))
			return
		super().accept()
