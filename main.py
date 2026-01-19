from __future__ import annotations

import sys
from pathlib import Path

from PyQt5.QtGui import QIcon

try:
	from PyQt5.QtWidgets import QApplication
except ModuleNotFoundError as e:
	if e.name == "PyQt5":
		print(
			"PyQt5 não está instalado no interpretador Python em uso.\n\n"
			"Como resolver (Windows/PowerShell):\n"
			"  1) Entre na pasta do projeto (onde está o requirements.txt):\n"
			"     cd \"C:\\Users\\Victor Hugo Azambuja\\Documents\\Financeiro\\FinancasPessoais\"\n"
			"  2) Ative o venv (se ainda não estiver ativo):\n"
			"     .\\venv\\Scripts\\Activate.ps1\n"
			"  3) Instale as dependências:\n"
			"     python -m pip install --upgrade pip\n"
			"     python -m pip install -r requirements.txt\n\n"
			"Alternativa: instalar usando caminho completo:\n"
			"  python -m pip install -r \"C:\\Users\\Victor Hugo Azambuja\\Documents\\Financeiro\\FinancasPessoais\\requirements.txt\"\n"
		)
		raise SystemExit(1)
	raise

from config import ensure_dirs, get_paths, setup_logging
from database.db_manager import DbManager
from ui.main_window import MainWindow
from ui.dialogs.login import LoginDialog
from ui.theme import apply_theme


def main() -> int:
	paths = get_paths()
	ensure_dirs(paths)
	setup_logging(paths)

	db = DbManager(paths.db_path)
	db.init_schema()

	app = QApplication(sys.argv)
	app.setApplicationName("GEFIPS")

	# Definir ícone do aplicativo (logo personalizada)
	logo_path = Path(__file__).resolve().parent / "logo" / "Gemini_Generated_Image_vwaqrtvwaqrtvwaq(1).png"
	if logo_path.exists():
		app.setWindowIcon(QIcon(str(logo_path)))
	apply_theme(app)

	# Mostrar diálogo de login
	login_dialog = LoginDialog(None, db)
	if login_dialog.exec_() != LoginDialog.Accepted:
		# Usuário cancelou o login
		return 0

	user_id = login_dialog.get_authenticated_user_id()
	if not user_id:
		# Falha na autenticação
		return 1

	# Login bem-sucedido, abrir janela principal
	win = MainWindow(db=db, current_user_id=user_id, exports_dir=paths.exports_dir, backup_dir=paths.backup_dir)
	win.show()

	return app.exec_()


if __name__ == "__main__":
	raise SystemExit(main())
