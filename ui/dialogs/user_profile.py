from __future__ import annotations

from typing import Optional

from PyQt5.QtWidgets import (
	QDialog,
	QVBoxLayout,
	QHBoxLayout,
	QLabel,
	QComboBox,
	QPushButton,
	QListWidget,
	QListWidgetItem,
	QMessageBox,
	QTabWidget,
	QLineEdit,
	QSpinBox,
	QCheckBox,
	QWidget,
)
from PyQt5.QtCore import Qt

from database.db_manager import DbManager
from database.models_user import User, FinancialProfile
from utils.auth import hash_password


class UserProfileDialog(QDialog):
	"""Dialog para seleção e gerenciamento de usuários e perfis financeiros"""

	def __init__(self, parent, db: DbManager, user_id: Optional[int] = None, skip_user_selection: bool = False):
		super().__init__(parent)
		self.db = db
		self.user_id = user_id
		self.skip_user_selection = skip_user_selection
		self.setWindowTitle("Selecione Perfil Financeiro" if skip_user_selection else "Selecione Usuário e Perfil")
		self.setGeometry(100, 100, 800, 600)
		self.selected_user_id = user_id  # Pre-filled se autenticado
		self.selected_profile_id = None

		# Tab widget para usuários e perfis
		tabs = QTabWidget()

		# Aba de Usuários (só mostra se não pulou seleção de usuário)
		if not skip_user_selection:
			user_tab = self._build_user_tab()
			tabs.addTab(user_tab, "Usuários")

		# Aba de Perfis Financeiros
		profile_tab = self._build_profile_tab()
		tabs.addTab(profile_tab, "Perfis Financeiros")

		# Botões de ação
		btn_layout = QHBoxLayout()
		btn_ok = QPushButton("✅ Confirmar")
		btn_ok.setMinimumHeight(40)
		btn_ok.setMinimumWidth(150)
		btn_ok.clicked.connect(self._on_accept)
		btn_cancel = QPushButton("❌ Cancelar")
		btn_cancel.setMinimumHeight(40)
		btn_cancel.setMinimumWidth(150)
		btn_cancel.clicked.connect(self.reject)
		btn_layout.addStretch()
		btn_layout.addWidget(btn_ok)
		btn_layout.addWidget(btn_cancel)

		# Layout principal
		main_layout = QVBoxLayout()
		main_layout.addWidget(tabs)
		main_layout.addLayout(btn_layout)
		self.setLayout(main_layout)

		# Status
		self.status_label = QLabel("Nenhum usuário/perfil selecionado")
		main_layout.insertWidget(0, self.status_label)

		if not skip_user_selection:
			self._refresh_users()
		self._refresh_profiles()

		# Se não há usuários, focar na criação
		if not skip_user_selection and len(self.db.list_users()) == 0:
			self.input_user_name.setFocus()
			QMessageBox.information(self, "Primeira Vez", "Crie um novo usuário e um perfil financeiro para começar")

	def _build_user_tab(self):
		layout = QVBoxLayout()

		# Lista de usuários
		layout.addWidget(QLabel("Usuários Disponíveis:"))
		self.user_list = QListWidget()
		self.user_list.itemClicked.connect(self._on_user_selected)
		layout.addWidget(self.user_list)

		# Campo novo usuário
		new_user_layout = QHBoxLayout()
		self.input_user_name = QLineEdit()
		self.input_user_name.setPlaceholderText("Nome do novo usuário")
		self.input_user_email = QLineEdit()
		self.input_user_email.setPlaceholderText("Email (opcional)")
		btn_add_user = QPushButton("➕ Novo Usuário")
		btn_add_user.setMinimumHeight(40)
		btn_add_user.setMinimumWidth(160)
		btn_add_user.clicked.connect(self._add_new_user)
		btn_delete_user = QPushButton("🗑️ Deletar")
		btn_delete_user.setMinimumHeight(40)
		btn_delete_user.setMinimumWidth(140)
		btn_delete_user.clicked.connect(self._delete_user)

		new_user_layout.addWidget(self.input_user_name)
		new_user_layout.addWidget(self.input_user_email)
		new_user_layout.addWidget(btn_add_user)
		new_user_layout.addWidget(btn_delete_user)

		layout.addLayout(new_user_layout)

		# Container
		container = QWidget()
		container.setLayout(layout)
		return container

	def _build_profile_tab(self):
		layout = QVBoxLayout()

		# Lista de perfis
		layout.addWidget(QLabel("Perfis Financeiros:"))
		self.profile_list = QListWidget()
		self.profile_list.itemClicked.connect(self._on_profile_selected)
		layout.addWidget(self.profile_list)

		# Campo novo perfil
		profile_form_layout = QHBoxLayout()
		self.input_profile_name = QLineEdit()
		self.input_profile_name.setPlaceholderText("Nome do novo perfil")

		self.input_profile_cdi = QSpinBox()
		self.input_profile_cdi.setRange(1, 100)
		self.input_profile_cdi.setValue(10)
		self.input_profile_cdi.setSuffix(" %CDI")

		self.check_ir = QCheckBox("IR Automático")
		self.check_ir.setChecked(True)

		self.check_iof = QCheckBox("IOF Automático")
		self.check_iof.setChecked(True)

		btn_add_profile = QPushButton("➕ Novo Perfil")
		btn_add_profile.setMinimumHeight(40)
		btn_add_profile.setMinimumWidth(160)
		btn_add_profile.clicked.connect(self._add_new_profile)

		btn_delete_profile = QPushButton("🗑️ Deletar")
		btn_delete_profile.setMinimumHeight(40)
		btn_delete_profile.setMinimumWidth(140)
		btn_delete_profile.clicked.connect(self._delete_profile)

		profile_form_layout.addWidget(QLabel("Nome:"))
		profile_form_layout.addWidget(self.input_profile_name)
		profile_form_layout.addWidget(QLabel("CDI Padrão:"))
		profile_form_layout.addWidget(self.input_profile_cdi)
		profile_form_layout.addWidget(self.check_ir)
		profile_form_layout.addWidget(self.check_iof)
		profile_form_layout.addWidget(btn_add_profile)
		profile_form_layout.addWidget(btn_delete_profile)

		layout.addLayout(profile_form_layout)

		# Container
		container = QWidget()
		container.setLayout(layout)
		return container

	def _refresh_users(self):
		self.user_list.clear()
		users = self.db.list_users()
		for user in users:
			item = QListWidgetItem(user.nome)
			item.setData(Qt.UserRole, user.id)
			self.user_list.addItem(item)

	def _refresh_profiles(self):
		self.profile_list.clear()
		if self.selected_user_id:
			profiles = self.db.list_user_financial_profiles(self.selected_user_id)
			for profile in profiles:
				item = QListWidgetItem(f"{profile.nome} ({profile.cdi_aa_padrao}% CDI)")
				item.setData(Qt.UserRole, profile.id)
				self.profile_list.addItem(item)

	def _on_user_selected(self, item):
		self.selected_user_id = item.data(Qt.UserRole)
		self._refresh_profiles()
		self._update_status()

	def _on_profile_selected(self, item):
		self.selected_profile_id = item.data(Qt.UserRole)
		self._update_status()

	def _update_status(self):
		if self.selected_user_id and self.selected_profile_id:
			user = self.db.get_user(self.selected_user_id)
			profile = self.db.get_financial_profile(self.selected_profile_id)
			self.status_label.setText(f"✓ Usuário: {user.nome} | Perfil: {profile.nome}")
		elif self.selected_user_id:
			user = self.db.get_user(self.selected_user_id)
			self.status_label.setText(f"Usuário: {user.nome} | Selecione um perfil")
		else:
			self.status_label.setText("Nenhum usuário/perfil selecionado")

	def _add_new_user(self):
		name = self.input_user_name.text().strip()
		if not name:
			QMessageBox.warning(self, "Validação", "Digite um nome para o usuário")
			return

		# Como esse método agora só é chamado após login (no modo skip_user_selection=True),
		# não deve ser mais acessível. Mantém compatibilidade com código anterior.
		if self.skip_user_selection:
			QMessageBox.warning(self, "Aviso", "Usuário já autenticado. Não é possível criar novo usuário agora.")
			return

		try:
			# Ao criar usuário sem autenticação prévia, não pedimos senha (serão criados sem proteção)
			# Isso é compatível com a primeira execução, quando não há usuários
			user = User(nome=name, email=self.input_user_email.text() or None, senha_hash="")
			self.db.add_user(user)
			self.input_user_name.clear()
			self.input_user_email.clear()
			self._refresh_users()
			QMessageBox.information(self, "Sucesso", f"Usuário '{name}' criado com sucesso.\n\nNota: Use a aba de Login para definir uma senha.")
		except Exception as e:
			QMessageBox.critical(self, "Erro", f"Falha ao criar usuário: {e}")

	def _delete_user(self):
		if not self.selected_user_id:
			QMessageBox.warning(self, "Aviso", "Selecione um usuário para deletar")
			return

		user = self.db.get_user(self.selected_user_id)
		reply = QMessageBox.question(
			self,
			"Confirmação",
			f"Deletar usuário '{user.nome}' e todos seus dados?\nISSO NÃO PODE SER DESFEITO!",
			QMessageBox.Yes | QMessageBox.No,
		)
		if reply == QMessageBox.Yes:
			try:
				self.db.delete_user(self.selected_user_id)
				self.selected_user_id = None
				self.selected_profile_id = None
				self._refresh_users()
				self._refresh_profiles()
				self._update_status()
				QMessageBox.information(self, "Sucesso", f"Usuário '{user.nome}' deletado")
			except Exception as e:
				QMessageBox.critical(self, "Erro", f"Falha ao deletar usuário: {e}")

	def _add_new_profile(self):
		if not self.selected_user_id:
			QMessageBox.warning(self, "Aviso", "Selecione um usuário primeiro")
			return

		name = self.input_profile_name.text().strip()
		if not name:
			QMessageBox.warning(self, "Validação", "Digite um nome para o perfil")
			return

		try:
			profile = FinancialProfile(
				user_id=self.selected_user_id,
				nome=name,
				cdi_aa_padrao=self.input_profile_cdi.value(),
				ir_automatico=self.check_ir.isChecked(),
				iof_automatico=self.check_iof.isChecked(),
			)
			self.db.add_financial_profile(profile)
			self.input_profile_name.clear()
			self._refresh_profiles()
			QMessageBox.information(self, "Sucesso", f"Perfil '{name}' criado com sucesso")
		except Exception as e:
			QMessageBox.critical(self, "Erro", f"Falha ao criar perfil: {e}")

	def _delete_profile(self):
		if not self.selected_profile_id:
			QMessageBox.warning(self, "Aviso", "Selecione um perfil para deletar")
			return

		profile = self.db.get_financial_profile(self.selected_profile_id)
		reply = QMessageBox.question(
			self,
			"Confirmação",
			f"Deletar perfil '{profile.nome}'?\nTodas as transações e cofrinhos serão removidos!\nISSO NÃO PODE SER DESFEITO!",
			QMessageBox.Yes | QMessageBox.No,
		)
		if reply == QMessageBox.Yes:
			try:
				self.db.delete_financial_profile(self.selected_profile_id)
				self.selected_profile_id = None
				self._refresh_profiles()
				self._update_status()
				QMessageBox.information(self, "Sucesso", f"Perfil '{profile.nome}' deletado")
			except Exception as e:
				QMessageBox.critical(self, "Erro", f"Falha ao deletar perfil: {e}")

	def _on_accept(self):
		"""Validar seleção antes de aceitar"""
		if not self.selected_user_id:
			QMessageBox.warning(self, "Aviso", "Selecione um usuário")
			return
		if not self.selected_profile_id:
			QMessageBox.warning(self, "Aviso", "Selecione um perfil financeiro")
			return
		self.accept()

	def get_selection(self):
		"""Retorna (user_id, profile_id) ou (None, None) se cancelado"""
		return self.selected_user_id, self.selected_profile_id
