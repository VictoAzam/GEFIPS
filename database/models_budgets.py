from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass(frozen=True)
class Budget:
	"""Modelo para orçamentos por categoria"""
	id: Optional[int]
	categoria: str
	limite_mensal: float
	mes: int  # 1-12
	ano: int
	ativo: bool = True
	descricao: Optional[str] = None


@dataclass(frozen=True)
class Goal:
	"""Modelo para metas financeiras"""
	id: Optional[int]
	nome: str
	valor_alvo: float
	valor_atual: float
	data_inicio: date
	data_alvo: date
	ativo: bool = True
	descricao: Optional[str] = None
	prioridade: str = "media"  # 'baixa', 'media', 'alta'
