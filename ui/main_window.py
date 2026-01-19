from __future__ import annotations

from datetime import date, datetime
from pathlib import Path

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import (
	QAction,
	QApplication,
	QComboBox,
	QFrame,
	QHBoxLayout,
	QHeaderView,
	QLabel,
	QMainWindow,
	QMessageBox,
	QFileDialog,
	QPushButton,
	QSizePolicy,
	QSpinBox,
	QStyle,
	QTableWidget,
	QTableWidgetItem,
	QTabWidget,
	QVBoxLayout,
	QWidget,
)

from database.db_manager import DbManager
from database.models import Transaction
from ui.charts_tab import ChartsTab
from ui.budgets_tab import BudgetsTab
from ui.goals_tab import GoalsTab
from ui.reports_tab import ReportsTab
from ui.dialogs.add_transaction import AddTransactionDialog
from ui.dialogs.user_profile import UserProfileDialog
from ui.icons import icon_add, icon_edit, icon_delete, icon_save, icon_moon, icon_sun, make_icon
from ui.piggy_tab import PiggyTab
from ui.theme import (
	apply_theme,
	get_palette,
	get_theme_scheme,
	is_dark_mode,
	set_theme_scheme,
	toggle_dark_mode,
)
from utils.tips import build_feedback
from utils.formatters import format_brl
from utils.reports import generate_monthly_report_pdf
from utils.backup import export_profile, restore_profile


_MONTHS_PT = [
	"Janeiro",
	"Fevereiro",
	"Março",
	"Abril",
	"Maio",
	"Junho",
	"Julho",
	"Agosto",
	"Setembro",
	"Outubro",
	"Novembro",
	"Dezembro",
]


class MainWindow(QMainWindow):
	def __init__(self, db: DbManager, current_user_id: int, exports_dir: Path, backup_dir: Path):
		super().__init__()
		self.db = db
		self.exports_dir = exports_dir
		self.backup_dir = backup_dir
		self.current_user_id = current_user_id

		self.setWindowTitle("GEFIPS - Gerenciador Financeiro Pessoal Simples")
		self.resize(980, 620)

		# Mostrar dialog de seleção de perfil (agora que usuário já está autenticado)
		dlg = UserProfileDialog(self, db, user_id=current_user_id, skip_user_selection=True)
		if dlg.exec_() != dlg.Accepted:
			raise RuntimeError("Nenhum perfil selecionado")

		user_id, profile_id = dlg.get_selection()
		if not profile_id:
			raise RuntimeError("Perfil financeiro é obrigatório")

		# Definir perfil no banco
		self.db.set_current_user(current_user_id)
		self.db.set_current_profile(profile_id)

		# Atualizar título
		user = self.db.get_user(current_user_id)
		profile = self.db.get_financial_profile(profile_id)
		self.setWindowTitle(f"GEFIPS - {user.nome} / {profile.nome}")

		self.tabs = QTabWidget()
		self.setCentralWidget(self.tabs)

		self.dashboard_tab = QWidget()
		self.tabs.addTab(self.dashboard_tab, "📊  Dashboard")

		self.charts_tab = ChartsTab(db=self.db)
		self.tabs.addTab(self.charts_tab, "📈  Gráficos")

		self.budgets_tab = BudgetsTab(db=self.db)
		self.tabs.addTab(self.budgets_tab, "💰  Orçamentos")

		self.goals_tab = GoalsTab(db=self.db)
		self.tabs.addTab(self.goals_tab, "🎯  Metas")

		self.reports_tab = ReportsTab(db=self.db)
		self.tabs.addTab(self.reports_tab, "📋  Relatórios")

		self.piggy_tab = PiggyTab(db=self.db, exports_dir=self.exports_dir)
		self.tabs.addTab(self.piggy_tab, "🏦  Cofrinhos")

		self._build_dashboard()
		self._build_actions()
		self.refresh()

	def _build_dashboard(self) -> None:
		today = date.today()
		style = self.style()

		# === HEADER COM LOGO ===
		header = QHBoxLayout()
		logo_path = Path(__file__).resolve().parent.parent / "logo" / "Gemini_Generated_Image_vwaqrtvwaqrtvwaq(1).png"
		if logo_path.exists():
			from PyQt5.QtGui import QPixmap
			logo_img = QLabel()
			pixmap = QPixmap(str(logo_path)).scaledToHeight(40, Qt.SmoothTransformation)
			logo_img.setPixmap(pixmap)
			header.addWidget(logo_img, 0, Qt.AlignLeft)

		header_title = QLabel("GEFIPS")
		header_title.setStyleSheet("font-size: 18px; font-weight: 700; color: #1E40AF;")
		header.addWidget(header_title, 1)
		header.addStretch()

		# Toggle dark mode
		self.btn_dark = QPushButton()
		if is_dark_mode():
			self.btn_dark.setIcon(make_icon(icon_sun(), 24, "#F1F5F9"))
			self.btn_dark.setText("☀️  Claro")
		else:
			self.btn_dark.setIcon(make_icon(icon_moon(), 24, "#111827"))
			self.btn_dark.setText("🌙  Escuro")
		self.btn_dark.clicked.connect(self.toggle_dark_theme)

		self.theme_combo = QComboBox()
		self.theme_combo.addItem("Neo-Fintech", "neo_fintech")
		self.theme_combo.addItem("Deep Focus", "deep_focus")
		self.theme_combo.addItem("Organic Growth", "organic_growth")
		self.theme_combo.setCurrentIndex(self.theme_combo.findData(get_theme_scheme()))
		self.theme_combo.currentIndexChanged.connect(self._on_theme_scheme_changed)

		self.btn_user_profile = QPushButton("👤  Usuário/Perfil")
		self.btn_user_profile.clicked.connect(self._show_user_profile_dialog)

		# Botões de Backup/Restauro
		self.btn_backup_export = QPushButton("💾  Backup")
		self.btn_backup_export.setIcon(self.style().standardIcon(QStyle.SP_DialogSaveButton))
		self.btn_backup_export.clicked.connect(self._export_backup)

		self.btn_backup_import = QPushButton("📥  Restaurar")
		self.btn_backup_import.setIcon(self.style().standardIcon(QStyle.SP_DialogOpenButton))
		self.btn_backup_import.clicked.connect(self._import_backup)

		header.addWidget(self.btn_user_profile)
		header.addSpacing(8)
		header.addWidget(self.btn_backup_export)
		header.addWidget(self.btn_backup_import)
		header.addSpacing(8)
		header.addWidget(self.theme_combo)
		header.addSpacing(6)
		header.addWidget(self.btn_dark)
		header.addSpacing(10)
		self.period_month = QComboBox()
		self.period_month.addItems(_MONTHS_PT)
		self.period_month.setSizeAdjustPolicy(QComboBox.AdjustToContents)
		self.period_month.setCurrentIndex(today.month - 1)
		self.period_month.currentIndexChanged.connect(lambda _i: self.refresh())

		self.period_year = QSpinBox()
		self.period_year.setRange(2000, 2100)
		self.period_year.setValue(today.year)
		self.period_year.valueChanged.connect(lambda _v: self.refresh())

		self.btn_report = QPushButton("Gerar relatório do mês")
		self.btn_report.setIcon(style.standardIcon(QStyle.SP_DialogSaveButton))
		self.btn_report.clicked.connect(self.generate_report_for_period)

		period_bar = QHBoxLayout()
		period_label = QLabel("📅  Período:")
		period_label.setObjectName("SectionTitle")
		period_label.setStyleSheet("font-weight: 700; font-size: 13px;")
		period_bar.addWidget(period_label)
		period_bar.addWidget(self.period_month)
		period_bar.addWidget(self.period_year)
		period_bar.addSpacing(12)
		period_bar.addWidget(self.btn_report)
		period_bar.addStretch(1)

		self.btn_add_entrada = QPushButton("➕  Adicionar Entrada")
		self.btn_add_entrada.setIcon(make_icon(icon_add(), 20, ("#F1F5F9" if is_dark_mode() else "#111827")))
		self.btn_add_entrada.clicked.connect(lambda: self.open_add_dialog("entrada"))

		self.btn_add_despesa = QPushButton("➖  Adicionar Despesa")
		self.btn_add_despesa.setIcon(make_icon(icon_add(), 20, ("#F1F5F9" if is_dark_mode() else "#111827")))
		self.btn_add_despesa.clicked.connect(lambda: self.open_add_dialog("saida"))

		self.btn_edit = QPushButton("✏️  Editar")
		self.btn_edit.setIcon(make_icon(icon_edit(), 20, ("#F1F5F9" if is_dark_mode() else "#111827")))
		self.btn_edit.clicked.connect(self.edit_selected)

		self.btn_delete = QPushButton("🗑️  Excluir")
		self.btn_delete.setIcon(make_icon(icon_delete(), 20, ("#F1F5F9" if is_dark_mode() else "#111827")))
		self.btn_delete.clicked.connect(self.delete_selected)

		# Ajustar tamanho dos botões conforme texto/ícone
		def _fit_buttons(btn_list):
			if not btn_list:
				return
			for btn in btn_list:
				hint = btn.sizeHint()
				btn.setMinimumWidth(hint.width() + 12)
				btn.setMinimumHeight(max(36, hint.height() + 6))
				btn.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed)

		_fit_buttons([
			self.btn_add_entrada,
			self.btn_add_despesa,
			self.btn_edit,
			self.btn_delete,
			self.btn_report,
			self.btn_user_profile,
			self.btn_backup_export,
			self.btn_backup_import,
			self.btn_dark,
		])

		self.lbl_saldo_mes = QLabel("—")
		self.lbl_entradas = QLabel("—")
		self.lbl_saidas = QLabel("—")
		self.lbl_tip_main = QLabel("—")
		self.lbl_tip_main.setWordWrap(True)
		self.lbl_tip_extras = QLabel("")
		self.lbl_tip_extras.setWordWrap(True)
		self.lbl_tip_extras.setStyleSheet("color: #64748B;")

		top = QHBoxLayout()
		top.addWidget(self._make_card("💰 Saldo do Mês", self.lbl_saldo_mes), stretch=2)
		top.addWidget(self._make_card("📈 Entradas", self.lbl_entradas))
		top.addWidget(self._make_card("📉 Saídas", self.lbl_saidas))
		top.addWidget(self._make_tip_card("💡 Dica do Mês", self.lbl_tip_main, self.lbl_tip_extras), stretch=3)

		self.table = QTableWidget(0, 5)
		self.table.setHorizontalHeaderLabels(["Data", "Tipo", "Categoria", "Descrição", "Valor"])
		self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
		self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
		self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
		self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
		self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
		self.table.setEditTriggers(QTableWidget.NoEditTriggers)
		self.table.setSelectionBehavior(QTableWidget.SelectRows)
		self.table.setSelectionMode(QTableWidget.SingleSelection)
		self.table.itemDoubleClicked.connect(lambda _it: self.edit_selected())

		btns = QHBoxLayout()
		btns.addWidget(self.btn_add_entrada)
		btns.addWidget(self.btn_add_despesa)
		btns.addSpacing(10)
		btns.addWidget(self.btn_edit)
		btns.addWidget(self.btn_delete)
		btns.addStretch(1)

		root = QVBoxLayout()
		root.addLayout(header)
		root.addSpacing(16)
		root.addLayout(period_bar)
		root.addSpacing(12)
		root.addLayout(top)
		root.addSpacing(12)
		self.section = QLabel("📊  Transações do mês:")
		section = self.section
		section.setObjectName("SectionTitle")
		root.addWidget(section)
		root.addWidget(self.table)
		root.addSpacing(12)
		root.addLayout(btns)

		self.dashboard_tab.setLayout(root)

	def _make_card(self, title: str, value_label: QLabel) -> QFrame:
		card = QFrame()
		card.setObjectName("Card")

		title_lbl = QLabel(title)
		title_lbl.setObjectName("CardTitle")
		value_label.setObjectName("CardValue")

		layout = QVBoxLayout(card)
		layout.setContentsMargins(14, 12, 14, 12)
		layout.setSpacing(6)
		layout.addWidget(title_lbl)
		layout.addWidget(value_label)
		return card

	def _make_tip_card(self, title: str, main_label: QLabel, extra_label: QLabel) -> QFrame:
		card = QFrame()
		card.setObjectName("Card")

		title_lbl = QLabel(title)
		title_lbl.setObjectName("CardTitle")
		main_label.setObjectName("CardValue")
		main_label.setWordWrap(True)
		extra_label.setWordWrap(True)

		layout = QVBoxLayout(card)
		layout.setContentsMargins(14, 12, 14, 12)
		layout.setSpacing(6)
		layout.addWidget(title_lbl)
		layout.addWidget(main_label)
		layout.addWidget(extra_label)
		return card

	def _build_actions(self) -> None:
		style = self.style()
		act_new = QAction("Nova transação", self)
		act_new.setIcon(style.standardIcon(QStyle.SP_FileIcon))
		act_new.setShortcut(QKeySequence("Ctrl+N"))
		act_new.triggered.connect(lambda: self.open_add_dialog(None))

		act_entrada = QAction("Nova entrada", self)
		act_entrada.setIcon(style.standardIcon(QStyle.SP_ArrowUp))
		act_entrada.setShortcut(QKeySequence("Ctrl+E"))
		act_entrada.triggered.connect(lambda: self.open_add_dialog("entrada"))

		act_saida = QAction("Nova despesa", self)
		act_saida.setIcon(style.standardIcon(QStyle.SP_ArrowDown))
		act_saida.setShortcut(QKeySequence("Ctrl+D"))
		act_saida.triggered.connect(lambda: self.open_add_dialog("saida"))

		self.addAction(act_new)
		self.addAction(act_entrada)
		self.addAction(act_saida)

	def open_add_dialog(self, tipo_predefinido):
		dlg = AddTransactionDialog(self, tipo_predefinido=tipo_predefinido)
		if dlg.exec_() != dlg.Accepted:
			return
		tx = dlg.transaction
		if tx is None:
			return
		plan = None
		try:
			plan = dlg.get_installment_plan()
		except Exception:
			plan = None

		if plan and plan.get("enabled") and tx.tipo == "saida":
			# Gerar N parcelas futuras não pagas
			num = int(plan.get("num") or 0)
			first_date = plan.get("first_date") or tx.data
			if num <= 1:
				self.db.add_transaction(tx)
				self.refresh()
				return
			# Cálculo do valor por parcela com ajuste no último
			total = float(tx.valor)
			base = round(total / num, 2)
			resto = round(total - base * num, 2)
			def _add_months(d: date, m: int) -> date:
				y = d.year + (d.month - 1 + m) // 12
				mo = (d.month - 1 + m) % 12 + 1
				day = min(d.day, [31, 29 if y % 4 == 0 and (y % 100 != 0 or y % 400 == 0) else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][mo - 1])
				return date(y, mo, day)
			for i in range(1, num + 1):
				valor_i = base
				if i == num:
					valor_i = round(base + resto, 2)
				dt_i = _add_months(first_date, i - 1)
				desc = f"Parcela {i}/{num} - {tx.descricao or tx.categoria}"
				p_tx = Transaction(
					id=None,
					tipo="saida",
					categoria=tx.categoria,
					subcategoria=None,
					descricao=desc,
					valor=float(valor_i),
					data=dt_i,
					pago=False,
					tags_json=tx.tags_json,
					anexo_caminho=None,
				)
				self.db.add_transaction(p_tx)
			self.refresh()
			return

		# Sem parcelamento, comportamento padrão
		self.db.add_transaction(tx)
		self.refresh()

	def _selected_tx_id(self):
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

	def edit_selected(self) -> None:
		tx_id = self._selected_tx_id()
		if tx_id is None:
			QMessageBox.information(self, "Editar", "Selecione uma transação na tabela.")
			return

		row = self.db.get_transaction(tx_id)
		if not row:
			QMessageBox.warning(self, "Editar", "Não foi possível encontrar essa transação.")
			return

		d = date.fromisoformat(str(row.get("data")))
		tx = Transaction(
			id=tx_id,
			tipo=str(row.get("tipo")),
			categoria=str(row.get("categoria")),
			subcategoria=row.get("subcategoria"),
			descricao=row.get("descricao"),
			valor=float(row.get("valor") or 0.0),
			data=d,
			pago=bool(row.get("pago")),
			tags_json=row.get("tags"),
			anexo_caminho=row.get("anexo_caminho"),
		)

		dlg = AddTransactionDialog(self, tipo_predefinido=tx.tipo, initial_tx=tx)
		if dlg.exec_() != dlg.Accepted:
			return
		new_tx = dlg.transaction
		if new_tx is None:
			return
		self.db.update_transaction(tx_id, new_tx)
		self.refresh()

	def delete_selected(self) -> None:
		tx_id = self._selected_tx_id()
		if tx_id is None:
			QMessageBox.information(self, "Excluir", "Selecione uma transação na tabela.")
			return

		resp = QMessageBox.question(
			self,
			"Excluir",
			"Tem certeza que deseja excluir a transação selecionada?",
			QMessageBox.Yes | QMessageBox.No,
			QMessageBox.No,
		)
		if resp != QMessageBox.Yes:
			return
		self.db.delete_transaction(tx_id)
		self.refresh()

	def refresh(self) -> None:
		year = int(self.period_year.value())
		month = int(self.period_month.currentIndex() + 1)
		entradas, saidas, saldo = self.db.get_month_balance(year, month)

		self.lbl_saldo_mes.setText(format_brl(saldo))
		self.lbl_entradas.setText(format_brl(entradas))
		self.lbl_saidas.setText(format_brl(saidas))

		self.lbl_saldo_mes.setProperty("positive", "true" if saldo >= 0 else "false")
		self.lbl_saldo_mes.setProperty("negative", "true" if saldo < 0 else "false")
		self.lbl_saldo_mes.style().unpolish(self.lbl_saldo_mes)
		self.lbl_saldo_mes.style().polish(self.lbl_saldo_mes)

		rows = self.db.list_month_transactions(year, month)
		self.section.setText(f"Transações do mês ({len(rows)}):")
		self.table.setRowCount(len(rows))
		for r, row in enumerate(rows):
			tx_id = int(row.get("id") or 0)
			data_txt = str(row.get("data", ""))
			tipo_txt = str(row.get("tipo", ""))
			cat_txt = str(row.get("categoria", ""))
			descr_txt = str(row.get("descricao") or "")
			valor = float(row.get("valor") or 0.0)

			items = [
				QTableWidgetItem(data_txt),
				QTableWidgetItem(tipo_txt),
				QTableWidgetItem(cat_txt),
				QTableWidgetItem(descr_txt),
				QTableWidgetItem(format_brl(valor)),
			]
			items[0].setData(Qt.UserRole, tx_id)
			for c, it in enumerate(items):
				if c == 4:
					it.setTextAlignment(int(Qt.AlignRight | Qt.AlignVCenter))
				self.table.setItem(r, c, it)

		self.charts_tab.refresh(year, month)
		self._update_tip(year, month, entradas, saidas, saldo)

	def _update_tip(self, year: int, month: int, entradas: float, saidas: float, saldo: float) -> None:
		# Top expense category
		top_expense = None
		cat_totals = self.db.get_month_category_totals(year, month, "saida")
		if cat_totals:
			row0 = cat_totals[0]
			top_expense = (str(row0.get("categoria") or ""), float(row0.get("total") or 0))

		# Last month expenses
		prev_year, prev_month = (year - 1, 12) if month == 1 else (year, month - 1)
		prev_entradas, prev_saidas, _ = self.db.get_month_balance(prev_year, prev_month)
		last_month_expense = prev_saidas if prev_saidas else None

		feedback = build_feedback(
			receita=entradas,
			despesa=saidas,
			saldo=saldo,
			top_expense=top_expense,
			last_month_expense=last_month_expense,
		)

		state = feedback.get("estado") or "equilibrado"
		main_text = feedback.get("dica") or "Mantenha o foco nas finanças."
		extras = feedback.get("extras") or []

		self.lbl_tip_main.setText(main_text)
		if extras:
			self.lbl_tip_extras.setText("\n".join(f"• {e}" for e in extras))
		else:
			self.lbl_tip_extras.setText("Nenhum alerta adicional.")

		palette = {
			"critico": "#DC2626",
			"alerta": "#F97316",
			"equilibrado": "#2563EB",
			"investidor": "#16A34A",
		}
		color = palette.get(state, "#2563EB")
		self.lbl_tip_main.setStyleSheet(f"color: {color}; font-weight: 700;")

	def generate_report_for_period(self) -> None:
		year = int(self.period_year.value())
		month = int(self.period_month.currentIndex() + 1)
		try:
			out = generate_monthly_report_pdf(
				db=self.db,
				exports_dir=self.exports_dir,
				year=year,
				month=month,
			)
		except Exception as e:
			QMessageBox.critical(self, "Relatório", f"Falha ao gerar relatório: {e}")
			return
		QMessageBox.information(self, "Relatório", f"Relatório gerado em:\n{out}")

	def _export_backup(self) -> None:
		try:
			# Sugestão de nome
			profile = self.db.get_financial_profile(self.db.current_profile_id)
			user = self.db.get_user(self.db.current_user_id)
			default_name = None
			if profile and user:
				uname = (user.nome or str(user.id)).replace(" ", "_")
				pname = (profile.nome or str(profile.id)).replace(" ", "_")
				ts = datetime.now().strftime("%Y%m%d-%H%M%S")
				default_name = f"backup_{uname}_{pname}_{ts}.json"

			# Caixa de diálogo para escolher destino
			start_dir = str(self.backup_dir)
			file_path, _ = QFileDialog.getSaveFileName(self, "Salvar Backup", start_dir + ("/" + (default_name or "backup.json")), "JSON (*.json)")
			if not file_path:
				return
			out = export_profile(
				db=self.db,
				backup_dir=Path(file_path).parent,
				user_id=int(self.db.current_user_id),
				profile_id=int(self.db.current_profile_id),
				filename=Path(file_path).name,
			)
		except Exception as e:
			QMessageBox.critical(self, "Backup", f"Falha ao exportar backup: {e}")
			return
		QMessageBox.information(self, "Backup", f"Backup salvo em:\n{out}")

	def _import_backup(self) -> None:
		try:
			start_dir = str(self.backup_dir)
			file_path, _ = QFileDialog.getOpenFileName(self, "Selecionar Backup", start_dir, "JSON (*.json)")
			if not file_path:
				return
			# Criar um novo perfil para dados restaurados
			new_profile_id = restore_profile(
				db=self.db,
				backup_file=Path(file_path),
				target_user_id=int(self.db.current_user_id),
			)
			# Alternar para o novo perfil
			self.db.set_current_profile(new_profile_id)
			# Atualizar título
			user = self.db.get_user(int(self.db.current_user_id))
			profile = self.db.get_financial_profile(int(new_profile_id))
			self.setWindowTitle(f"GEFIPS - {user.nome} / {profile.nome}")
			# Atualizar dados
			self.refresh()
		except Exception as e:
			QMessageBox.critical(self, "Restaurar", f"Falha ao restaurar backup: {e}")
			return

	def toggle_dark_theme(self) -> None:
		toggle_dark_mode()
		self._apply_theme()

	def _on_theme_scheme_changed(self, index: int) -> None:
		scheme = self.theme_combo.itemData(index)
		if not scheme:
			return
		set_theme_scheme(scheme)
		self._apply_theme()

	def _apply_theme(self) -> None:
		app = QApplication.instance()
		apply_theme(app)
		palette = get_palette()
		icon_color = palette.get("text", "#111827")
		
		self.btn_add_entrada.setIcon(make_icon(icon_add(), 20, icon_color))
		self.btn_add_despesa.setIcon(make_icon(icon_add(), 20, icon_color))
		self.btn_edit.setIcon(make_icon(icon_edit(), 20, icon_color))
		self.btn_delete.setIcon(make_icon(icon_delete(), 20, icon_color))
		
		dark = is_dark_mode()
		if dark:
			self.btn_dark.setIcon(make_icon(icon_sun(), 24, "#F1F5F9"))
			self.btn_dark.setText("Claro")
		else:
			self.btn_dark.setIcon(make_icon(icon_moon(), 24, "#111827"))
			self.btn_dark.setText("Escuro")

		if hasattr(self, 'piggy_tab') and self.piggy_tab:
			self._refresh_piggy_tab_theme(icon_color)

	def _refresh_piggy_tab_theme(self, icon_color: str) -> None:
		if hasattr(self.piggy_tab, 'btn_add'):
			self.piggy_tab.btn_add.setIcon(make_icon(icon_add(), 20, icon_color))
		if hasattr(self.piggy_tab, 'btn_edit'):
			self.piggy_tab.btn_edit.setIcon(make_icon(icon_edit(), 20, icon_color))
		if hasattr(self.piggy_tab, 'btn_delete'):
			self.piggy_tab.btn_delete.setIcon(make_icon(icon_delete(), 20, icon_color))
		if hasattr(self.piggy_tab, 'btn_report'):
			self.piggy_tab.btn_report.setIcon(make_icon(icon_save(), 20, icon_color))

	def _show_user_profile_dialog(self) -> None:
		dlg = UserProfileDialog(self, self.db)
		if dlg.exec_() != dlg.Accepted:
			return

		user_id, profile_id = dlg.get_selection()
		if not user_id or not profile_id:
			QMessageBox.warning(self, "Aviso", "Selecione um usuário e um perfil")
			return

		# Definir novo usuário/perfil
		self.db.set_current_user(user_id)
		self.db.set_current_profile(profile_id)

		# Atualizar título
		user = self.db.get_user(user_id)
		profile = self.db.get_financial_profile(profile_id)
		self.setWindowTitle(f"Meu Controle Financeiro v1.0 - {user.nome} / {profile.nome}")

		# Atualizar dados
		self.refresh()


