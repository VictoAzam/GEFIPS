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
	QDateEdit,
	QProgressBar,
)
from PyQt5.QtGui import QColor, QFont
from PyQt5.QtCore import QDate

from database.db_manager import DbManager
from database.models_budgets import Goal
from utils.formatters import format_brl


_PRIORITY_COLORS = {
	"alta": "#FEE2E2",
	"media": "#FEF3C7",
	"baixa": "#DBEAFE",
}

_PRIORITY_LABELS = {
	"alta": "🔴 Alta",
	"media": "🟡 Média",
	"baixa": "🟢 Baixa",
}


class GoalsTab(QWidget):
	def __init__(self, db: DbManager):
		super().__init__()
		self.db = db
		
		self.title = QLabel("Metas Financeiras")
		self.title.setObjectName("SectionTitle")
		
		# Tabela de metas
		self.table = QTableWidget()
		self.table.setColumnCount(6)
		self.table.setHorizontalHeaderLabels(["Meta", "Alvo", "Atual", "Progresso", "Prioridade", "Data Alvo"])
		self.table.setAlternatingRowColors(True)
		
		# Configurar largura das colunas
		header = self.table.horizontalHeader()
		header.setStretchLastSection(False)
		header.setSectionResizeMode(0, QHeaderView.Stretch)  # Meta estica
		header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # Alvo
		header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Atual
		header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Progresso auto
		header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Prioridade auto
		header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # Data auto
		header.setMinimumSectionSize(90)
		
		# Altura das linhas
		self.table.verticalHeader().setDefaultSectionSize(40)
		
		# Botões
		buttons_layout = QHBoxLayout()
		add_btn = QPushButton("Adicionar Meta")
		add_btn.clicked.connect(self._show_add_goal_dialog)
		edit_btn = QPushButton("Editar")
		edit_btn.clicked.connect(self._edit_goal)
		delete_btn = QPushButton("Deletar")
		delete_btn.clicked.connect(self._delete_goal)

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
		root.addWidget(self.table, stretch=1)
		root.addLayout(buttons_layout)
		self.setLayout(root)
		
		self._refresh_goals()
	
	def _refresh_goals(self) -> None:
		"""Atualiza a tabela com as metas"""
		goals = self.db.list_goals(ativas_apenas=False)
		
		self.table.setRowCount(len(goals))
		
		for row, goal in enumerate(goals):
			# Armazenar ID na primeira coluna (invisível)
			nome = QTableWidgetItem(goal["nome"])
			nome.setData(Qt.UserRole, goal["id"])  # Armazena o ID
			
			alvo = QTableWidgetItem(format_brl(goal["valor_alvo"]))
			alvo.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
			
			atual = QTableWidgetItem(format_brl(goal["valor_atual"]))
			atual.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
			
			# Barra de progresso
			percentual = (goal["valor_atual"] / goal["valor_alvo"] * 100) if goal["valor_alvo"] > 0 else 0
			progresso = QProgressBar()
			progresso.setValue(int(min(100, percentual)))
			progresso.setFormat(f"{percentual:.1f}%")
			
			# Estilizar barra de progresso
			if percentual >= 100:
				progresso.setStyleSheet("QProgressBar::chunk { background-color: #10B981; }")
			elif percentual >= 50:
				progresso.setStyleSheet("QProgressBar::chunk { background-color: #3B82F6; }")
			else:
				progresso.setStyleSheet("QProgressBar::chunk { background-color: #F59E0B; }")
			
			# Prioridade com cores melhoradas
			prioridade_texto = {
				"alta": "ALTA",
				"media": "MÉDIA",
				"baixa": "BAIXA"
			}.get(goal["prioridade"], goal["prioridade"].upper())
			
			prioridade = QTableWidgetItem(prioridade_texto)
			prioridade.setTextAlignment(Qt.AlignCenter)
			
			# Cores mais fortes e texto branco
			if goal["prioridade"] == "alta":
				prioridade.setBackground(QColor("#DC2626"))  # Vermelho forte
				prioridade.setForeground(QColor("#FFFFFF"))
			elif goal["prioridade"] == "media":
				prioridade.setBackground(QColor("#F59E0B"))  # Laranja forte
				prioridade.setForeground(QColor("#FFFFFF"))
			else:
				prioridade.setBackground(QColor("#3B82F6"))  # Azul forte
				prioridade.setForeground(QColor("#FFFFFF"))
			
			font = prioridade.font()
			font.setBold(True)
			prioridade.setFont(font)
			
			data_alvo = QTableWidgetItem(goal["data_alvo"])
			data_alvo.setTextAlignment(Qt.AlignCenter)
			
			self.table.setItem(row, 0, nome)
			self.table.setItem(row, 1, alvo)
			self.table.setItem(row, 2, atual)
			self.table.setCellWidget(row, 3, progresso)
			self.table.setItem(row, 4, prioridade)
			self.table.setItem(row, 5, data_alvo)

		self.table.resizeColumnsToContents()
	
	def _show_add_goal_dialog(self) -> None:
		"""Mostra diálogo para adicionar nova meta"""
		dialog = GoalDialog(self, self.db)
		if dialog.exec_() == QDialog.Accepted:
			self._refresh_goals()
	
	def _edit_goal(self) -> None:
		"""Edita meta selecionada"""
		current_row = self.table.currentRow()
		if current_row < 0:
			QMessageBox.warning(self, "Aviso", "Selecione uma meta para editar")
			return
		
		# Obter ID da meta
		goal_id = self.table.item(current_row, 0).data(Qt.UserRole)
		goal_data = self.db.get_goal(goal_id)
		
		if not goal_data:
			QMessageBox.critical(self, "Erro", "Meta não encontrada")
			return
		
		# Abrir diálogo de edição
		dialog = GoalDialog(self, self.db, goal_id=goal_id, goal_data=goal_data)
		if dialog.exec_() == QDialog.Accepted:
			self._refresh_goals()
	
	def _delete_goal(self) -> None:
		"""Deleta meta selecionada"""
		current_row = self.table.currentRow()
		if current_row < 0:
			QMessageBox.warning(self, "Aviso", "Selecione uma meta para deletar")
			return
		
		# Obter ID e nome da meta
		goal_id = self.table.item(current_row, 0).data(Qt.UserRole)
		nome = self.table.item(current_row, 0).text()
		
		reply = QMessageBox.question(
			self, 
			"Confirmar", 
			f"Deletar meta '{nome}'?",
			QMessageBox.Yes | QMessageBox.No
		)
		
		if reply == QMessageBox.Yes:
			try:
				self.db.delete_goal(goal_id)
				QMessageBox.information(self, "Sucesso", "Meta deletada com sucesso!")
				self._refresh_goals()
			except Exception as e:
				QMessageBox.critical(self, "Erro", f"Erro ao deletar meta: {str(e)}")


class GoalDialog(QDialog):
	def __init__(self, parent, db: DbManager, goal_id: int = None, goal_data: Dict[str, Any] = None):
		super().__init__(parent)
		self.db = db
		self.goal_id = goal_id
		self.is_edit = goal_id is not None
		
		self.setWindowTitle("Editar Meta Financeira" if self.is_edit else "Nova Meta Financeira")
		self.setGeometry(100, 100, 500, 400)
		
		layout = QFormLayout()
		
		self.nome_input = QLineEdit()
		layout.addRow("Nome da Meta:", self.nome_input)
		
		self.alvo_input = QDoubleSpinBox()
		self.alvo_input.setMaximum(9999999.99)
		layout.addRow("Valor Alvo (R$):", self.alvo_input)
		
		self.atual_input = QDoubleSpinBox()
		self.atual_input.setMaximum(9999999.99)
		layout.addRow("Valor Atual (R$):", self.atual_input)
		
		self.data_inicio_input = QDateEdit()
		self.data_inicio_input.setDate(QDate.currentDate())
		layout.addRow("Data Início:", self.data_inicio_input)
		
		self.data_alvo_input = QDateEdit()
		self.data_alvo_input.setDate(QDate.currentDate().addMonths(6))
		layout.addRow("Data Alvo:", self.data_alvo_input)
		
		self.prioridade_combo = QComboBox()
		self.prioridade_combo.addItems(["baixa", "media", "alta"])
		self.prioridade_combo.setCurrentText("media")
		layout.addRow("Prioridade:", self.prioridade_combo)
		
		self.descricao_input = QLineEdit()
		layout.addRow("Descrição:", self.descricao_input)
		
		self.ativo_check = QCheckBox("Meta ativa")
		self.ativo_check.setChecked(True)
		layout.addRow("", self.ativo_check)
		
		# Preencher com dados existentes se for edição
		if self.is_edit and goal_data:
			self.nome_input.setText(goal_data["nome"])
			self.alvo_input.setValue(float(goal_data["valor_alvo"]))
			self.atual_input.setValue(float(goal_data["valor_atual"]))
			
			# Converter strings de data para QDate
			from datetime import datetime
			data_inicio = datetime.fromisoformat(goal_data["data_inicio"]).date()
			data_alvo = datetime.fromisoformat(goal_data["data_alvo"]).date()
			
			self.data_inicio_input.setDate(QDate(data_inicio.year, data_inicio.month, data_inicio.day))
			self.data_alvo_input.setDate(QDate(data_alvo.year, data_alvo.month, data_alvo.day))
			self.prioridade_combo.setCurrentText(goal_data["prioridade"])
			self.descricao_input.setText(goal_data.get("descricao") or "")
			self.ativo_check.setChecked(bool(goal_data["ativo"]))
		
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
		"""Valida e salva a meta"""
		nome = self.nome_input.text().strip()
		alvo = self.alvo_input.value()
		atual = self.atual_input.value()
		
		if not nome:
			QMessageBox.warning(self, "Erro", "Nome da meta não pode estar vazio")
			return
		
		if alvo <= 0:
			QMessageBox.warning(self, "Erro", "Valor alvo deve ser maior que zero")
			return
		
		if atual < 0:
			QMessageBox.warning(self, "Erro", "Valor atual não pode ser negativo")
			return
		
		try:
			goal = Goal(
				id=None,
				nome=nome,
				valor_alvo=alvo,
				valor_atual=atual,
				data_inicio=self.data_inicio_input.date().toPyDate(),
				data_alvo=self.data_alvo_input.date().toPyDate(),
				ativo=self.ativo_check.isChecked(),
				descricao=self.descricao_input.text().strip() or None,
				prioridade=self.prioridade_combo.currentText(),
			)
			
			if self.is_edit:
				self.db.update_goal(self.goal_id, goal)
				QMessageBox.information(self, "Sucesso", "Meta atualizada com sucesso!")
			else:
				self.db.add_goal(goal)
				QMessageBox.information(self, "Sucesso", "Meta criada com sucesso!")
			
			super().accept()
		except Exception as e:
			QMessageBox.critical(self, "Erro", f"Erro ao salvar meta: {str(e)}")
