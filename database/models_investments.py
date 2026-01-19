from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass(frozen=True)
class PiggyBank:
	id: Optional[int]
	nome: str
	instituicao: str
	percent_cdi: float  # ex.: 100 a 120
	cdi_aa: float  # CDI anual em % a.a. (ex.: 10.65)
	principal: float
	aporte_mensal: float = 0.0
	data_inicio: date = date.today()
	aplicar_impostos: bool = False
