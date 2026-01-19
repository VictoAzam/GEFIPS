from __future__ import annotations

from datetime import date
from typing import Any, Dict, List

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
	QFrame,
	QHBoxLayout,
	QHeaderView,
	QLabel,
	QPushButton,
	QSizePolicy,
	QSpinBox,
	QTableWidget,
	QTableWidgetItem,
	QVBoxLayout,
	QWidget,
	QMessageBox,
	QDialog,
	QFormLayout,
	QLineEdit,
	QCheckBox,
	QDoubleSpinBox,
	QComboBox,
)
from PyQt5.QtGui import QColor

from database.db_manager import DbManager
from database.models_budgets import Budget
from utils.formatters import format_brl


class BudgetsTab(QWidget):
	def __init__(self, db: DbManager):
		super().__init__()
		self.db = db
		
		self.title = QLabel("Orçamentos por Categoria")
		self.title.setObjectName("SectionTitle")
		
		# Mês e ano
		month_year_layout = QHBoxLayout()
		month_year_layout.addWidget(QLabel("Mês:"))
		self.month_spinbox = QSpinBox()
		self.month_spinbox.setMinimum(1)
		self.month_spinbox.setMaximum(12)
		self.month_spinbox.setValue(date.today().month)
		self.month_spinbox.valueChanged.connect(self._refresh_budgets)
		month_year_layout.addWidget(self.month_spinbox)
		
		month_year_layout.addWidget(QLabel("Ano:"))
		self.year_spinbox = QSpinBox()
		self.year_spinbox.setMinimum(2020)
		self.year_spinbox.setMaximum(2050)
		self.year_spinbox.setValue(date.today().year)
		self.year_spinbox.valueChanged.connect(self._refresh_budgets)
		month_year_layout.addWidget(self.year_spinbox)
		month_year_layout.addStretch()
		
		# Tabela de orçamentos
		self.table = QTableWidget()
		self.table.setColumnCount(5)
		self.table.setHorizontalHeaderLabels(["Categoria", "Limite", "Gasto", "Restante", "Status"])
		self.table.setAlternatingRowColors(True)
		
		# Configurar largura das colunas
		header = self.table.horizontalHeader()
		header.setStretchLastSection(False)
		header.setSectionResizeMode(0, QHeaderView.Stretch)  # Categoria estica
		header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # Limite
		header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Gasto
		header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Restante
		header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Status auto
		header.setMinimumSectionSize(90)
		
		# Altura das linhas
		self.table.verticalHeader().setDefaultSectionSize(35)
		
		# Botões
		buttons_layout = QHBoxLayout()
		add_btn = QPushButton("Adicionar Orçamento")
		add_btn.clicked.connect(self._show_add_budget_dialog)
		edit_btn = QPushButton("Editar")
		edit_btn.clicked.connect(self._edit_budget)
		delete_btn = QPushButton("Deletar")
		delete_btn.clicked.connect(self._delete_budget)

		def _auto_size_buttons(btns):
			for btn in btns:
				hint = btn.sizeHint()
				btn.setMinimumWidth(hint.width() + 10)
				btn.setMinimumHeight(max(34, hint.height() + 4))
				btn.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed)

		_auto_size_buttons([add_btn, edit_btn, delete_btn])
		
		buttons_layout.addWidget(add_btn)
		buttons_layout.addWidget(edit_btn)
		buttons_layout.addWidget(delete_btn)
		buttons_layout.addStretch()
		
		# Layout principal
		root = QVBoxLayout()
		root.addWidget(self.title)
		root.addLayout(month_year_layout)
		root.addWidget(self.table, stretch=1)
		root.addLayout(buttons_layout)
		self.setLayout(root)
		
		self._refresh_budgets()
	
	def _refresh_budgets(self) -> None:
		"""Atualiza a tabela com os orçamentos"""
		mes = self.month_spinbox.value()
		ano = self.year_spinbox.value()
		
		summary = self.db.get_budget_summary(ano, mes)
		
		self.table.setRowCount(len(summary))
		
		for row, budget_info in enumerate(summary):
			categoria = QTableWidgetItem(budget_info["categoria"])
			categoria.setData(Qt.UserRole, budget_info["id"])  # Armazena o ID
			
			limite = QTableWidgetItem(format_brl(budget_info["limite_mensal"]))
			limite.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
			
			gasto = QTableWidgetItem(format_brl(budget_info["gasto_atual"]))
			gasto.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
			
			restante = budget_info["limite_mensal"] - budget_info["gasto_atual"]
			restante_item = QTableWidgetItem(format_brl(restante))
			restante_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
			
			# Criar célula de status com cores melhores
			if budget_info["excedido"]:
				status = QTableWidgetItem("EXCEDIDO")
				status.setBackground(QColor("#DC2626"))  # Vermelho forte
				status.setForeground(QColor("#FFFFFF"))  # Texto branco
				restante_item.setForeground(QColor("#DC2626"))
			else:
				percentual = (budget_info["gasto_atual"] / budget_info["limite_mensal"] * 100) if budget_info["limite_mensal"] > 0 else 0
				if percentual > 75:
					status = QTableWidgetItem("ATENÇÃO")
					status.setBackground(QColor("#F59E0B"))  # Laranja/Amarelo forte
					status.setForeground(QColor("#FFFFFF"))
					restante_item.setForeground(QColor("#D97706"))
				else:
					status = QTableWidgetItem("OK")
					status.setBackground(QColor("#10B981"))  # Verde forte
					status.setForeground(QColor("#FFFFFF"))
					restante_item.setForeground(QColor("#059669"))
			
			status.setTextAlignment(Qt.AlignCenter)
			from PyQt5.QtGui import QFont
			font = status.font()
			font.setBold(True)
			status.setFont(font)
			
			self.table.setItem(row, 0, categoria)
			self.table.setItem(row, 1, limite)
			self.table.setItem(row, 2, gasto)
			self.table.setItem(row, 3, restante_item)
			self.table.setItem(row, 4, status)

		self.table.resizeColumnsToContents()
	
	def _show_add_budget_dialog(self) -> None:
		"""Mostra diálogo para adicionar novo orçamento"""
		mes = self.month_spinbox.value()
		ano = self.year_spinbox.value()
		dialog = BudgetDialog(self, self.db, mes=mes, ano=ano)
		if dialog.exec_() == QDialog.Accepted:
			self._refresh_budgets()
	
	def _edit_budget(self) -> None:
		"""Edita orçamento selecionado"""
		current_row = self.table.currentRow()
		if current_row < 0:
			QMessageBox.warning(self, "Aviso", "Selecione um orçamento para editar")
			return
		
		# Obter ID do orçamento
		budget_id = self.table.item(current_row, 0).data(Qt.UserRole)
		budget_data = self.db.get_budget(budget_id)
		
		if not budget_data:
			QMessageBox.critical(self, "Erro", "Orçamento não encontrado")
			return
		
		mes = self.month_spinbox.value()
		ano = self.year_spinbox.value()
		
		# Abrir diálogo de edição
		dialog = BudgetDialog(self, self.db, mes=mes, ano=ano, budget_id=budget_id, budget_data=budget_data)
		if dialog.exec_() == QDialog.Accepted:
			self._refresh_budgets()
	
	def _delete_budget(self) -> None:
		"""Deleta orçamento selecionado"""
		current_row = self.table.currentRow()
		if current_row < 0:
			QMessageBox.warning(self, "Aviso", "Selecione um orçamento para deletar")
			return
		
		# Obter ID e categoria
		budget_id = self.table.item(current_row, 0).data(Qt.UserRole)
		categoria = self.table.item(current_row, 0).text()
		
		reply = QMessageBox.question(
			self, 
			"Confirmar", 
			f"Deletar orçamento para '{categoria}'?",
			QMessageBox.Yes | QMessageBox.No
		)
		
		if reply == QMessageBox.Yes:
			try:
				self.db.delete_budget(budget_id)
				QMessageBox.information(self, "Sucesso", "Orçamento deletado com sucesso!")
				self._refresh_budgets()
			except Exception as e:
				QMessageBox.critical(self, "Erro", f"Erro ao deletar orçamento: {str(e)}")


class BudgetDialog(QDialog):
	def __init__(self, parent, db: DbManager, mes: int, ano: int, budget_id: int = None, budget_data: Dict[str, Any] = None):
		super().__init__(parent)
		self.db = db
		self.mes = mes
		self.ano = ano
		self.budget_id = budget_id
		self.is_edit = budget_id is not None
		
		self.setWindowTitle("Editar Orçamento" if self.is_edit else "Novo Orçamento")
		self.setGeometry(100, 100, 400, 300)
		
		layout = QFormLayout()
		
		self.categoria_input = QLineEdit()
		layout.addRow("Categoria:", self.categoria_input)
		
		self.limite_input = QDoubleSpinBox()
		self.limite_input.setMaximum(999999.99)
		layout.addRow("Limite Mensal (R$):", self.limite_input)
		
		self.ativo_check = QCheckBox("Orçamento ativo")
		self.ativo_check.setChecked(True)
		layout.addRow("", self.ativo_check)
		
		self.descricao_input = QLineEdit()
		layout.addRow("Descrição:", self.descricao_input)
		
		# Preencher com dados existentes se for edição
		if self.is_edit and budget_data:
			self.categoria_input.setText(budget_data["categoria"])
			self.limite_input.setValue(float(budget_data["limite_mensal"]))
			self.ativo_check.setChecked(bool(budget_data["ativo"]))
			self.descricao_input.setText(budget_data.get("descricao") or "")
		
		buttons_layout = QHBoxLayout()
		ok_btn = QPushButton("Salvar")
		ok_btn.clicked.connect(self.accept)
		cancel_btn = QPushButton("Cancelar")
		cancel_btn.clicked.connect(self.reject)

		for btn in (ok_btn, cancel_btn):
			hint = btn.sizeHint()
			btn.setMinimumWidth(hint.width() + 8)
			btn.setMinimumHeight(max(32, hint.height() + 4))
			btn.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed)
		buttons_layout.addWidget(ok_btn)
		buttons_layout.addWidget(cancel_btn)
		
		layout.addRow(buttons_layout)
		self.setLayout(layout)
	
	def accept(self) -> None:
		"""Valida e salva o orçamento"""
		categoria = self.categoria_input.text().strip()
		limite = self.limite_input.value()
		
		if not categoria:
			QMessageBox.warning(self, "Erro", "Categoria não pode estar vazia")
			return
		
		if limite <= 0:
			QMessageBox.warning(self, "Erro", "Limite deve ser maior que zero")
			return
		
		try:
			budget = Budget(
				id=None,
				categoria=categoria,
				limite_mensal=limite,
				mes=self.mes,
				ano=self.ano,
				ativo=self.ativo_check.isChecked(),
				descricao=self.descricao_input.text().strip() or None,
			)
			
			if self.is_edit:
				self.db.update_budget(self.budget_id, budget)
				QMessageBox.information(self, "Sucesso", "Orçamento atualizado com sucesso!")
			else:
				self.db.add_budget(budget)
				QMessageBox.information(self, "Sucesso", "Orçamento criado com sucesso!")
			
			super().accept()
		except Exception as e:
			QMessageBox.critical(self, "Erro", f"Erro ao salvar orçamento: {str(e)}")
