from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import List

from dateutil.relativedelta import relativedelta


@dataclass(frozen=True)
class ProjectionPoint:
	ref_date: date
	months: int
	total_aportes: float
	saldo_bruto: float
	rendimento_bruto: float
	iof: float
	ir: float
	saldo_liquido: float


def annual_rate_from_cdi(cdi_aa_percent: float, percent_cdi: float) -> float:
	"""Retorna taxa efetiva anual (decimal). Ex.: 10.65% a.a. e 110% do CDI."""
	cdi = max(0.0, float(cdi_aa_percent)) / 100.0
	mult = max(0.0, float(percent_cdi)) / 100.0
	return cdi * mult


def monthly_rate_from_annual(annual_rate: float) -> float:
	"""Converte taxa efetiva anual (decimal) em taxa efetiva mensal (decimal)."""
	return (1.0 + float(annual_rate)) ** (1.0 / 12.0) - 1.0


def ir_rate_by_days(days: int) -> float:
	"""Tabela regressiva (Brasil) sobre rendimento. Retorna alíquota (0-1)."""
	if days <= 180:
		return 0.225
	if days <= 360:
		return 0.20
	if days <= 720:
		return 0.175
	return 0.15


def iof_rate_by_days(days: int) -> float:
	"""IOF regressivo (apenas se resgate <30 dias). Aproximação linear (0->1)."""
	if days >= 30:
		return 0.0
	# dia 1 ~ 96%, dia 30 = 0% (tabela real não é linear, mas serve pro MVP)
	# Mantém simples e previsível.
	return max(0.0, (30 - max(1, days)) / 29.0)


def project_piggy(
	start: date,
	principal: float,
	aporte_mensal: float,
	annual_rate: float,
	horizon_months: int = 12,
	aplicar_impostos: bool = False,
) -> List[ProjectionPoint]:
	"""Projeção mês a mês com juros compostos (aprox. taxa mensal derivada do anual).

	Assunções MVP:
	- Aporte mensal entra no início de cada mês.
	- Impostos (IR/IOF) são calculados como se houvesse resgate em cada ponto.
	"""
	principal = float(principal)
	aporte_mensal = float(aporte_mensal)
	monthly_rate = monthly_rate_from_annual(annual_rate)

	saldo = principal
	total_aportes = principal
	points: List[ProjectionPoint] = []

	for m in range(1, int(horizon_months) + 1):
		# aporte no início do mês
		if aporte_mensal > 0:
			saldo += aporte_mensal
			total_aportes += aporte_mensal

		# juros no mês
		saldo *= 1.0 + monthly_rate

		ref = start + relativedelta(months=+m)
		days = max(1, (ref - start).days)

		rendimento = max(0.0, saldo - total_aportes)
		iof = 0.0
		ir = 0.0
		saldo_liq = saldo
		if aplicar_impostos and rendimento > 0:
			iof = rendimento * iof_rate_by_days(days)
			r_base = max(0.0, rendimento - iof)
			ir = r_base * ir_rate_by_days(days)
			saldo_liq = total_aportes + max(0.0, rendimento - iof - ir)

		points.append(
			ProjectionPoint(
				ref_date=ref,
				months=m,
				total_aportes=total_aportes,
				saldo_bruto=saldo,
				rendimento_bruto=rendimento,
				iof=iof,
				ir=ir,
				saldo_liquido=saldo_liq,
			)
		)

	return points
