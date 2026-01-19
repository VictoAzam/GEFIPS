from __future__ import annotations

from pathlib import Path

from PyQt5.QtWidgets import QApplication


_DARK_MODE = False
_ACTIVE_SCHEME = "neo_fintech"


_THEMES = {
	"neo_fintech": {
		"label": "Neo-Fintech",
		"light": {
			"bg": "#F8FAFC",
			"surface": "#FFFFFF",
			"primary": "#6366F1",
			"accent": "#14B8A6",
			"text": "#1E293B",
			"muted": "#64748B",
			"border": "#E2E8F0",
			"focus": "#14B8A6",
			"success": "#10B981",
			"danger": "#F43F5E",
			"tab_hover": "rgba(99, 102, 241, 0.10)",
			"selection_bg_table": "rgba(20, 184, 166, 0.15)",
			"disabled_bg": "#F1F5F9",
		},
		"dark": {
			"bg": "#0F172A",
			"surface": "#1E293B",
			"primary": "#818CF8",
			"accent": "#14B8A6",
			"text": "#F1F5F9",
			"muted": "#94A3B8",
			"border": "#334155",
			"focus": "#14B8A6",
			"success": "#34D399",
			"danger": "#FB7185",
			"tab_hover": "rgba(129, 140, 248, 0.18)",
			"selection_bg_table": "rgba(129, 140, 248, 0.22)",
			"disabled_bg": "#334155",
		},
	},
	"deep_focus": {
		"label": "Deep Focus",
		"light": {
			"bg": "#FFFFFF",
			"surface": "#F3F4F6",
			"primary": "#7C3AED",
			"accent": "#7C3AED",
			"text": "#111827",
			"muted": "#6B7280",
			"border": "#E5E7EB",
			"focus": "#7C3AED",
			"success": "#059669",
			"danger": "#DC2626",
			"tab_hover": "rgba(124, 58, 237, 0.12)",
			"selection_bg_table": "rgba(124, 58, 237, 0.18)",
			"disabled_bg": "#F3F4F6",
		},
		"dark": {
			"bg": "#121212",
			"surface": "#1E1E1E",
			"primary": "#A78BFA",
			"accent": "#A78BFA",
			"text": "#E5E7EB",
			"muted": "#9CA3AF",
			"border": "#2C2C2C",
			"focus": "#A78BFA",
			"success": "#6EE7B7",
			"danger": "#F87171",
			"tab_hover": "rgba(167, 139, 250, 0.25)",
			"selection_bg_table": "rgba(167, 139, 250, 0.28)",
			"disabled_bg": "#2C2C2C",
		},
	},
	"organic_growth": {
		"label": "Organic Growth",
		"light": {
			"bg": "#FDFCF8",
			"surface": "#FFFFFF",
			"primary": "#0D9488",
			"accent": "#F59E0B",
			"text": "#262626",
			"muted": "#525252",
			"border": "#E5E7EB",
			"focus": "#0D9488",
			"success": "#16A34A",
			"danger": "#E11D48",
			"tab_hover": "rgba(13, 148, 136, 0.12)",
			"selection_bg_table": "rgba(13, 148, 136, 0.16)",
			"disabled_bg": "#F3F4F6",
		},
		"dark": {
			"bg": "#11181C",
			"surface": "#18212F",
			"primary": "#2DD4BF",
			"accent": "#F59E0B",
			"text": "#ECEDEE",
			"muted": "#94A3B8",
			"border": "#243040",
			"focus": "#2DD4BF",
			"success": "#4ADE80",
			"danger": "#FB7185",
			"tab_hover": "rgba(45, 212, 191, 0.20)",
			"selection_bg_table": "rgba(45, 212, 191, 0.24)",
			"disabled_bg": "#1F2A37",
		},
	},
}

def stylesheet() -> str:
	return stylesheet_dark() if _DARK_MODE else stylesheet_light()


def set_theme_scheme(name: str) -> None:
	"""Define o esquema de cores ativo (neo_fintech, deep_focus, organic_growth)."""
	global _ACTIVE_SCHEME
	if name in _THEMES:
		_ACTIVE_SCHEME = name


def get_theme_scheme() -> str:
	return _ACTIVE_SCHEME


def get_palette() -> dict:
	"""Retorna o dicionário da paleta atual considerando modo claro/escuro."""
	return dict(_palette(_DARK_MODE))


def apply_theme(app: QApplication) -> None:
	app.setStyleSheet(stylesheet())


def toggle_dark_mode() -> None:
	global _DARK_MODE
	_DARK_MODE = not _DARK_MODE


def set_dark_mode(enabled: bool) -> None:
	global _DARK_MODE
	_DARK_MODE = bool(enabled)


def is_dark_mode() -> bool:
	return _DARK_MODE


def stylesheet_light() -> str:
	return _build_styles(_palette(False))


def stylesheet_dark() -> str:
	return _build_styles(_palette(True))


def _palette(dark: bool) -> dict:
	theme = _THEMES.get(_ACTIVE_SCHEME, _THEMES["neo_fintech"])
	return theme["dark" if dark else "light"]


def _build_styles(palette: dict) -> str:
	primary = palette["primary"]
	accent = palette.get("accent", primary)
	success = palette.get("success", "#10B981")
	danger = palette.get("danger", "#EF4444")
	bg = palette["bg"]
	surface = palette["surface"]
	text = palette["text"]
	muted = palette.get("muted", text)
	border = palette.get("border", primary)
	focus = palette.get("focus", accent)
	tab_hover = palette.get("tab_hover", f"rgba(0,0,0,0.08)")
	selection_bg_table = palette.get("selection_bg_table", "rgba(14, 165, 233, 0.15)")
	disabled_bg = palette.get("disabled_bg", "#F1F5F9")
	btn_pressed = palette.get("primary_pressed", primary)

	return f"""
	QWidget {{
		color: {text};
		background: {bg};
	}}

	QMainWindow {{
		background: {bg};
	}}

	QMainWindow::separator {{
		background: {border};
		width: 1px;
		height: 1px;
	}}

	/* === ABAS === */
	QTabWidget::pane {{
		border: none;
		background: {surface};
		border-radius: 16px;
		margin: 8px;
	}}

	QTabBar::tab {{
		background: transparent;
		border: none;
		padding: 14px 22px;
		margin-right: 8px;
		border-radius: 12px 12px 0 0;
		color: {muted};
		font-weight: 600;
		font-size: 13px;
		letter-spacing: 0.5px;
		min-width: 120px;
		white-space: nowrap;
	}}
	QTabBar::tab:hover {{
		background: {tab_hover};
		color: {text};
	}}
	QTabBar::tab:selected {{
		background: {primary};
		color: #FFFFFF;
		border-bottom: 3px solid {primary};
	}}

	/* === SEÇÕES === */
	QLabel#SectionTitle {{
		color: {text};
		font-weight: 700;
		font-size: 14px;
		padding-top: 12px;
		padding-bottom: 6px;
		letter-spacing: 0.3px;
	}}

	/* === CARDS === */
	QFrame#Card {{
		background: {surface};
		border: 1px solid {border};
		border-radius: 16px;
	}}
	QFrame#Card:hover {{
		background: {surface};
	}}
	QLabel#CardTitle {{
		color: {muted};
		font-weight: 600;
		font-size: 11px;
		letter-spacing: 0.5px;
		text-transform: uppercase;
	}}
	QLabel#CardValue {{
		color: {text};
		font-size: 22px;
		font-weight: 700;
	}}
	QLabel#CardValue[positive="true"] {{
		color: {success};
	}}
	QLabel#CardValue[negative="true"] {{
		color: {danger};
	}}

	/* === BOTÕES === */
	QPushButton {{
		background: {surface};
		border: 1px solid {border};
		border-radius: 12px;
		padding: 12px 16px;
		min-width: 140px;
		min-height: 40px;
		font-weight: 600;
		font-size: 11px;
		color: {text};
		letter-spacing: 0.3px;
		white-space: nowrap;
	}}
	QPushButton:hover {{
		background: {primary};
		border-color: {primary};
		color: #FFFFFF;
	}}
	QPushButton:pressed {{
		background: {btn_pressed};
		border-color: {btn_pressed};
	}}
	QPushButton:disabled {{
		color: {muted};
		background: {disabled_bg};
		border-color: {border};
	}}

	/* === INPUTS === */
	QLineEdit, QPlainTextEdit, QComboBox, QDateEdit, QDoubleSpinBox, QSpinBox {{
		background: {surface};
		border: 1px solid {border};
		border-radius: 16px;
		padding: 10px 14px;
		color: {text};
		font-size: 12px;
		selection-background-color: {accent};
	}}
	QLineEdit:focus, QPlainTextEdit:focus, QComboBox:focus, QDateEdit:focus, QDoubleSpinBox:focus, QSpinBox:focus {{
		border: 2px solid {focus};
	}}
	QComboBox::drop-down {{
		border: none;
	}}
	QComboBox::down-arrow {{
		image: url(noimg);
		width: 0;
		height: 0;
	}}

	/* === DIÁLOGOS === */
	QDialog {{
		background: {bg};
	}}
	QDialogButtonBox QPushButton {{
		min-width: 120px;
		padding: 10px 16px;
	}}

	/* === TABELAS === */
	QTableWidget {{
		background: {surface};
		border: none;
		border-radius: 12px;
		gridline-color: {border};
		selection-background-color: {selection_bg_table};
		selection-color: {text};
		font-size: 12px;
		color: {text};
	}}
	QTableWidget::item {{
		padding: 8px 10px;
		border: none;
		border-bottom: 1px solid {border};
	}}
	QTableWidget::item:alternate {{
		background: rgba(241, 245, 249, 0.6);
	}}
	QTableWidget::item:selected {{
		background: {selection_bg_table};
		color: {text};
	}}
	QHeaderView::section {{
		background: {primary};
		color: #FFFFFF;
		border: none;
		padding: 10px 12px;
		font-weight: 700;
		font-size: 11px;
		letter-spacing: 0.5px;
		text-transform: uppercase;
		border-radius: 0;
	}}

	/* === CHECKBOXES === */
	QCheckBox {{
		color: {text};
		spacing: 6px;
	}}
	QCheckBox::indicator {{
		width: 18px;
		height: 18px;
		border-radius: 4px;
	}}
	QCheckBox::indicator:unchecked {{
		background: {surface};
		border: 2px solid {border};
	}}
	QCheckBox::indicator:checked {{
		background: {primary};
		border: 2px solid {primary};
	}}

	/* === SCROLL BARS === */
	QScrollBar:vertical {{
		background: {bg};
		width: 8px;
		border: none;
	}}
	QScrollBar::handle:vertical {{
		background: {muted};
		border-radius: 4px;
		min-height: 20px;
	}}
	QScrollBar::handle:vertical:hover {{
		background: {primary};
	}}
	"""


