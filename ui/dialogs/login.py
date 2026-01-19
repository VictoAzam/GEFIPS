from __future__ import annotations

from PyQt5.QtWidgets import (
	QDialog,
	QVBoxLayout,
	QHBoxLayout,
	QLabel,
	QLineEdit,
	QPushButton,
	QMessageBox,
	QTabWidget,
)
from PyQt5.QtCore import Qt

from database.db_manager import DbManager
from database.models_user import User
from utils.auth import hash_password, verify_password


class LoginDialog(QDialog):
	"""Dialog para login de usuário"""

	def __init__(self, parent, db: DbManager):
		super().__init__(parent)
		self.db = db
		self.setWindowTitle("Login")
		self.setGeometry(200, 200, 500, 450)
		self.authenticated_user_id = None

		# Tab widget para login e novo usuário
		tabs = QTabWidget()

		# Aba de Login
		login_tab = self._build_login_tab()
		tabs.addTab(login_tab, "Login")

		# Aba de Novo Usuário
		new_user_tab = self._build_new_user_tab()
		tabs.addTab(new_user_tab, "Novo Usuário")

		# Layout principal
		main_layout = QVBoxLayout()
		main_layout.addWidget(tabs)
		self.setLayout(main_layout)

	def _build_login_tab(self):
		layout = QVBoxLayout()

		# Campos de login
		layout.addWidget(QLabel("Usuário:"))
		self.login_username = QLineEdit()
		self.login_username.setPlaceholderText("Nome do usuário")
		layout.addWidget(self.login_username)

		layout.addWidget(QLabel("Senha:"))
		self.login_password = QLineEdit()
		self.login_password.setPlaceholderText("Senha")
		self.login_password.setEchoMode(QLineEdit.Password)
		layout.addWidget(self.login_password)

		layout.addSpacing(10)

		# Botões
		btn_layout = QHBoxLayout()
		btn_login = QPushButton("✅ Entrar")
		btn_login.setMinimumHeight(40)
		btn_login.setMinimumWidth(150)
		btn_login.clicked.connect(self._do_login)
		btn_cancel = QPushButton("❌ Cancelar")
		btn_cancel.setMinimumHeight(40)
		btn_cancel.setMinimumWidth(150)
		btn_cancel.clicked.connect(self.reject)
		btn_layout.addWidget(btn_login)
		btn_layout.addWidget(btn_cancel)

		layout.addLayout(btn_layout)
		layout.addStretch()

		# Container
		from PyQt5.QtWidgets import QWidget
		container = QWidget()
		container.setLayout(layout)
		return container

	def _build_new_user_tab(self):
		layout = QVBoxLayout()

		layout.addWidget(QLabel("Nome de usuário:"))
		self.new_username = QLineEdit()
		self.new_username.setPlaceholderText("Escolha um nome único")
		layout.addWidget(self.new_username)

		layout.addWidget(QLabel("Email (opcional):"))
		self.new_email = QLineEdit()
		self.new_email.setPlaceholderText("seu@email.com")
		layout.addWidget(self.new_email)

		layout.addWidget(QLabel("Senha:"))
		self.new_password = QLineEdit()
		self.new_password.setPlaceholderText("Mínimo 6 caracteres")
		self.new_password.setEchoMode(QLineEdit.Password)
		layout.addWidget(self.new_password)

		layout.addWidget(QLabel("Confirmar Senha:"))
		self.new_password_confirm = QLineEdit()
		self.new_password_confirm.setPlaceholderText("Confirme a senha")
		self.new_password_confirm.setEchoMode(QLineEdit.Password)
		layout.addWidget(self.new_password_confirm)

		layout.addSpacing(10)

		# Botões
		btn_layout = QHBoxLayout()
		btn_create = QPushButton("✅ Criar Usuário")
		btn_create.setMinimumHeight(40)
		btn_create.setMinimumWidth(150)
		btn_create.clicked.connect(self._create_user)
		btn_cancel = QPushButton("❌ Cancelar")
		btn_cancel.setMinimumHeight(40)
		btn_cancel.setMinimumWidth(150)
		btn_cancel.clicked.connect(self.reject)
		btn_layout.addWidget(btn_create)
		btn_layout.addWidget(btn_cancel)

		layout.addLayout(btn_layout)
		layout.addStretch()

		# Container
		from PyQt5.QtWidgets import QWidget
		container = QWidget()
		container.setLayout(layout)
		return container

	def _do_login(self):
		"""Fazer login com usuário/senha"""
		username = self.login_username.text().strip()
		password = self.login_password.text()

		if not username or not password:
			QMessageBox.warning(self, "Aviso", "Digite usuário e senha")
			return

		# Buscar usuário
		user = self.db.get_user_by_name(username)
		if not user:
			QMessageBox.critical(self, "Erro", "Usuário não encontrado")
			self.login_password.clear()
			return

		# Verificar senha
		if not verify_password(password, user.senha_hash):
			QMessageBox.critical(self, "Erro", "Senha incorreta")
			self.login_password.clear()
			return

		# Login bem-sucedido
		self.authenticated_user_id = user.id
		QMessageBox.information(self, "Sucesso", f"Bem-vindo, {user.nome}!")
		self.accept()

	def _create_user(self):
		"""Criar novo usuário"""
		username = self.new_username.text().strip()
		email = self.new_email.text().strip() or None
		password = self.new_password.text()
		password_confirm = self.new_password_confirm.text()

		# Validações
		if not username:
			QMessageBox.warning(self, "Aviso", "Digite um nome de usuário")
			return

		if len(password) < 6:
			QMessageBox.warning(self, "Aviso", "Senha deve ter pelo menos 6 caracteres")
			return

		if password != password_confirm:
			QMessageBox.warning(self, "Aviso", "As senhas não coincidem")
			return

		# Verificar se usuário já existe
		if self.db.get_user_by_name(username):
			QMessageBox.critical(self, "Erro", "Esse nome de usuário já existe")
			return

		try:
			# Hash da senha
			password_hash = hash_password(password)

			# Criar usuário
			user = User(nome=username, email=email, senha_hash=password_hash)
			user_id = self.db.add_user(user)

			QMessageBox.information(self, "Sucesso", f"Usuário '{username}' criado com sucesso!\nFaça login para continuar")

			# Limpar campos
			self.new_username.clear()
			self.new_email.clear()
			self.new_password.clear()
			self.new_password_confirm.clear()

		except Exception as e:
			QMessageBox.critical(self, "Erro", f"Falha ao criar usuário: {e}")

	def get_authenticated_user_id(self) -> int:
		"""Retorna o ID do usuário autenticado"""
		return self.authenticated_user_id
