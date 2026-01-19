from __future__ import annotations

from datetime import date, timedelta
from typing import Any, Dict, List

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
	QFrame,
	QHBoxLayout,
	QLabel,
	QPushButton,
	QSpinBox,
	QVBoxLayout,
	QWidget,
	QTabWidget,
)

from database.db_manager import DbManager
from utils.formatters import format_brl


_PRIMARY = "#2E86AB"
_SECONDARY = "#18A999"
_DANGER = "#DC2626"
_MUTED = "#6B7280"


class ReportsTab(QWidget):
	def __init__(self, db: DbManager):
		super().__init__()
		self.db = db
		
		self.title = QLabel("Relatórios")
		self.title.setObjectName("SectionTitle")
		
		# Mês e ano
		month_year_layout = QHBoxLayout()
		month_year_layout.addWidget(QLabel("Mês:"))
		self.month_spinbox = QSpinBox()
		self.month_spinbox.setMinimum(1)
		self.month_spinbox.setMaximum(12)
		self.month_spinbox.setValue(date.today().month)
		self.month_spinbox.valueChanged.connect(self._refresh_reports)
		month_year_layout.addWidget(self.month_spinbox)
		
		month_year_layout.addWidget(QLabel("Ano:"))
		self.year_spinbox = QSpinBox()
		self.year_spinbox.setMinimum(2020)
		self.year_spinbox.setMaximum(2050)
		self.year_spinbox.setValue(date.today().year)
		self.year_spinbox.valueChanged.connect(self._refresh_reports)
		month_year_layout.addWidget(self.year_spinbox)
		month_year_layout.addStretch()
		
		# Abas de relatórios
		self.tabs = QTabWidget()
		
		# Aba de gráficos mensais
		self.monthly_chart_frame = QFrame()
		self.monthly_chart_frame.setObjectName("Card")
		self.monthly_chart_layout = QVBoxLayout(self.monthly_chart_frame)
		self.tabs.addTab(self.monthly_chart_frame, "Gráficos Mensais")
		
		# Aba de comparação anual
		self.annual_chart_frame = QFrame()
		self.annual_chart_frame.setObjectName("Card")
		self.annual_chart_layout = QVBoxLayout(self.annual_chart_frame)
		self.tabs.addTab(self.annual_chart_frame, "Comparação Anual")
		
		# Aba de resumo
		self.summary_frame = QFrame()
		self.summary_frame.setObjectName("Card")
		self.summary_layout = QVBoxLayout(self.summary_frame)
		self.tabs.addTab(self.summary_frame, "Resumo Mensal")
		
		# Layout principal
		root = QVBoxLayout()
		root.addWidget(self.title)
		root.addLayout(month_year_layout)
		root.addWidget(self.tabs, stretch=1)
		self.setLayout(root)
		
		self._refresh_reports()
	
	def _refresh_reports(self) -> None:
		"""Atualiza todos os relatórios"""
		mes = self.month_spinbox.value()
		ano = self.year_spinbox.value()
		
		self._create_monthly_charts(ano, mes)
		self._create_annual_comparison(ano)
		self._create_summary(ano, mes)
	
	def _create_monthly_charts(self, ano: int, mes: int) -> None:
		"""Cria gráficos do mês"""
		# Limpar layout anterior
		for i in reversed(range(self.monthly_chart_layout.count())):
			self.monthly_chart_layout.itemAt(i).widget().setParent(None)
		
		# Dados
		entradas, saidas, saldo = self.db.get_month_balance(ano, mes)
		category_totals = self.db.get_month_category_totals(ano, mes, "saida")
		daily_totals = self.db.get_month_daily_totals(ano, mes)
		
		# Figura com 2 subplots
		fig = Figure(figsize=(10, 4), dpi=100)
		fig.suptitle(f"Análise de {self._get_month_name(mes)}/{ano}", fontsize=14, fontweight='bold')
		
		# Gráfico 1: Entradas vs Saídas
		ax1 = fig.add_subplot(1, 2, 1)
		labels = ["Entradas", "Saídas"]
		values = [entradas, saidas]
		colors = [_SECONDARY, _DANGER]
		ax1.bar(labels, values, color=colors)
		ax1.set_ylabel("Valor (R$)")
		ax1.set_title("Entradas vs Saídas")
		for i, v in enumerate(values):
			ax1.text(i, v + saidas * 0.02, format_brl(v), ha='center', fontweight='bold')
		
		# Gráfico 2: Gastos por categoria
		ax2 = fig.add_subplot(1, 2, 2)
		if category_totals:
			cats = [c["categoria"] for c in category_totals[:5]]
			vals = [c["total"] for c in category_totals[:5]]
			ax2.barh(cats, vals, color=_PRIMARY)
			ax2.set_xlabel("Valor (R$)")
			ax2.set_title("Top 5 Categorias de Gasto")
			for i, v in enumerate(vals):
				ax2.text(v + max(vals) * 0.02, i, format_brl(v), va='center')
		else:
			ax2.text(0.5, 0.5, "Sem dados", ha='center', va='center', transform=ax2.transAxes)
		
		fig.tight_layout()
		
		canvas = FigureCanvas(fig)
		self.monthly_chart_layout.addWidget(canvas)
	
	def _create_annual_comparison(self, ano: int) -> None:
		"""Cria gráfico de comparação anual"""
		# Limpar layout anterior
		for i in reversed(range(self.annual_chart_layout.count())):
			self.annual_chart_layout.itemAt(i).widget().setParent(None)
		
		# Dados para todos os meses do ano
		meses_nomes = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
		entradas_list = []
		saidas_list = []
		
		for mes in range(1, 13):
			entradas, saidas, _ = self.db.get_month_balance(ano, mes)
			entradas_list.append(entradas)
			saidas_list.append(saidas)
		
		# Gráfico
		fig = Figure(figsize=(10, 3), dpi=100)
		fig.suptitle(f"Análise Anual - {ano}", fontsize=14, fontweight='bold')
		
		ax = fig.add_subplot(1, 1, 1)
		x_pos = range(len(meses_nomes))
		width = 0.35
		
		ax.bar([x - width/2 for x in x_pos], entradas_list, width, label="Entradas", color=_SECONDARY)
		ax.bar([x + width/2 for x in x_pos], saidas_list, width, label="Saídas", color=_DANGER)
		
		ax.set_xlabel("Mês")
		ax.set_ylabel("Valor (R$)")
		ax.set_xticks(x_pos)
		ax.set_xticklabels(meses_nomes)
		ax.legend()
		ax.grid(axis='y', alpha=0.3)
		
		fig.tight_layout()
		
		canvas = FigureCanvas(fig)
		self.annual_chart_layout.addWidget(canvas)
	
	def _create_summary(self, ano: int, mes: int) -> None:
		"""Cria resumo mensal"""
		# Limpar layout anterior
		for i in reversed(range(self.summary_layout.count())):
			widget = self.summary_layout.itemAt(i).widget()
			if widget:
				widget.setParent(None)
		
		# Dados
		entradas, saidas, saldo = self.db.get_month_balance(ano, mes)
		category_totals = self.db.get_month_category_totals(ano, mes, "saida")
		
		# Criar widgets de resumo
		summary_text = f"""
		<h3>Resumo de {self._get_month_name(mes)}/{ano}</h3>
		<table style="width: 100%; border-collapse: collapse;">
		<tr style="background-color: #F3F4F6;">
			<td style="padding: 10px;"><b>Entradas:</b></td>
			<td style="padding: 10px; text-align: right; color: {_SECONDARY};"><b>{format_brl(entradas)}</b></td>
		</tr>
		<tr>
			<td style="padding: 10px;"><b>Saídas:</b></td>
			<td style="padding: 10px; text-align: right; color: {_DANGER};"><b>{format_brl(saidas)}</b></td>
		</tr>
		<tr style="background-color: #F3F4F6;">
			<td style="padding: 10px;"><b>Saldo:</b></td>
			<td style="padding: 10px; text-align: right; color: {'green' if saldo >= 0 else 'red'};"><b>{format_brl(saldo)}</b></td>
		</tr>
		</table>
		
		<h4 style="margin-top: 20px;">Gastos por Categoria</h4>
		<table style="width: 100%; border-collapse: collapse;">
		"""
		
		for cat_info in category_totals:
			categoria = cat_info["categoria"]
			total = cat_info["total"]
			percentual = (total / saidas * 100) if saidas > 0 else 0
			summary_text += f"""
			<tr>
				<td style="padding: 8px;">{categoria}</td>
				<td style="padding: 8px; text-align: right;">{format_brl(total)}</td>
				<td style="padding: 8px; text-align: right; color: #6B7280;">{percentual:.1f}%</td>
			</tr>
			"""
		
		summary_text += "</table>"
		
		label = QLabel(summary_text)
		label.setWordWrap(True)
		self.summary_layout.addWidget(label)
		self.summary_layout.addStretch()
	
	def _get_month_name(self, mes: int) -> str:
		"""Retorna o nome do mês em português"""
		meses = [
			"Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
			"Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
		]
		return meses[mes - 1] if 1 <= mes <= 12 else "Mês"
