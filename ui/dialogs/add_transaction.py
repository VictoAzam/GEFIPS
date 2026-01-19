from __future__ import annotations

from datetime import date
import json
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
	QPlainTextEdit,
	QMessageBox,
	QSpinBox,
	QVBoxLayout,
)

from database.models import Transaction
from utils.validators import require_non_empty, require_positive


class AddTransactionDialog(QDialog):
	def __init__(
		self,
		parent=None,
		tipo_predefinido: Optional[str] = None,
		initial_tx: Optional[Transaction] = None,
	):
		super().__init__(parent)
		self.setWindowTitle("Editar Transação" if initial_tx else "Adicionar Transação")
		self.setModal(True)
		self._tx: Optional[Transaction] = None

		self.tipo = QComboBox()
		self.tipo.addItems(["entrada", "saida"])
		if initial_tx:
			self.tipo.setCurrentText(initial_tx.tipo)
		elif tipo_predefinido in ("entrada", "saida"):
			self.tipo.setCurrentText(tipo_predefinido)

		self.categoria = QLineEdit()
		self.categoria.setPlaceholderText("Ex.: Salário, Mercado, Internet...")

		self.descricao = QLineEdit()
		self.descricao.setPlaceholderText("Opcional")

		self.valor = QDoubleSpinBox()
		self.valor.setDecimals(2)
		self.valor.setMinimum(0.01)
		self.valor.setMaximum(1_000_000_000.00)
		self.valor.setSingleStep(10.0)

		self.data = QDateEdit()
		self.data.setCalendarPopup(True)
		self.data.setDate(QDate.currentDate())

		self.pago = QCheckBox("Pago/Recebido")
		self.pago.setChecked(True)

		# Parcelamento
		self.parcelado = QCheckBox("Parcelar despesa")
		self.parcelado.setChecked(False)
		self.num_parcelas = QSpinBox()
		self.num_parcelas.setRange(2, 36)
		self.num_parcelas.setValue(2)
		self.primeira_parcela = QDateEdit()
		self.primeira_parcela.setCalendarPopup(True)
		# default: mesma data da transação (permite parcelar no mesmo mês se necessário)
		self.primeira_parcela.setDate(QDate.currentDate())
		# Habilitar/Desabilitar campos conforme checkbox
		def _toggle_parcelado(state: bool):
			self.num_parcelas.setEnabled(state)
			self.primeira_parcela.setEnabled(state)
			# Atualizar primeira parcela conforme a data da transação
			if state:
				self.primeira_parcela.setDate(self.data.date())
		_toggle_parcelado(False)
		self.parcelado.toggled.connect(_toggle_parcelado)
		# Quando a data da transação muda, atualizar também a primeira parcela
		self.data.dateChanged.connect(lambda qd: self.primeira_parcela.setDate(qd) if self.parcelado.isChecked() else None)

		self.tags = QLineEdit()
		self.tags.setPlaceholderText("Separar por vírgula (opcional)")

		self.notas = QPlainTextEdit()
		self.notas.setPlaceholderText("Notas (opcional)")

		form = QFormLayout()
		form.addRow("Tipo:", self.tipo)
		form.addRow("Categoria:", self.categoria)
		form.addRow("Descrição:", self.descricao)
		form.addRow("Valor (R$):", self.valor)
		form.addRow("Data:", self.data)
		form.addRow("", self.pago)
		form.addRow("", self.parcelado)
		form.addRow("Nº parcelas:", self.num_parcelas)
		form.addRow("Primeira parcela em:", self.primeira_parcela)
		form.addRow("Tags:", self.tags)
		form.addRow("Notas:", self.notas)

		btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
		btns.accepted.connect(self.accept)
		btns.rejected.connect(self.reject)

		root = QVBoxLayout()
		root.addLayout(form)
		root.addWidget(btns)
		self.setLayout(root)

		if initial_tx:
			self._populate_from(initial_tx)

	def _populate_from(self, tx: Transaction) -> None:
		self.categoria.setText(tx.categoria or "")
		self.descricao.setText(tx.descricao or "")
		self.valor.setValue(float(tx.valor or 0.0))
		self.data.setDate(QDate(tx.data.year, tx.data.month, tx.data.day))
		self.pago.setChecked(bool(tx.pago))

		if tx.tags_json:
			try:
				parsed = json.loads(tx.tags_json)
				if isinstance(parsed, list):
					self.tags.setText(", ".join(str(x) for x in parsed if str(x).strip()))
			except Exception:
				self.tags.setText(str(tx.tags_json))

	@property
	def transaction(self) -> Optional[Transaction]:
		return self._tx

	def get_installment_plan(self):
		"""Retorna plano de parcelamento se habilitado; caso contrário, None.
		Estrutura: {enabled: bool, num: int, first_date: date}
		"""
		if not self.parcelado.isChecked():
			return None
		qd = self.primeira_parcela.date()
		first = date(qd.year(), qd.month(), qd.day())
		return {
			"enabled": True,
			"num": int(self.num_parcelas.value()),
			"first_date": first,
		}

	def accept(self) -> None:
		try:
			self._tx = self.build_transaction()
		except ValueError as e:
			QMessageBox.warning(self, "Validação", str(e))
			return
		super().accept()

	def build_transaction(self) -> Transaction:
		tipo = self.tipo.currentText()
		categoria = require_non_empty(self.categoria.text(), "Categoria")
		valor = require_positive(float(self.valor.value()), "Valor")

		qd = self.data.date()
		d = date(qd.year(), qd.month(), qd.day())

		descricao = (self.descricao.text() or "").strip() or None

		tags_text = (self.tags.text() or "").strip()
		tags_json = None
		if tags_text:
			parts = [p.strip() for p in tags_text.split(",") if p.strip()]
			tags_json = "[" + ",".join(f'"{p}"' for p in parts) + "]" if parts else None

		return Transaction(
			id=None,
			tipo=tipo,
			categoria=categoria,
			subcategoria=None,
			descricao=descricao,
			valor=valor,
			data=d,
			pago=self.pago.isChecked(),
			tags_json=tags_json,
			anexo_caminho=None,
		)
