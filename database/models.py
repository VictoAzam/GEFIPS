from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass(frozen=True)
class Transaction:
	id: Optional[int]
	tipo: str  # 'entrada' | 'saida'
	categoria: str
	subcategoria: Optional[str]
	descricao: Optional[str]
	valor: float
	data: date
	pago: bool = True
	tags_json: Optional[str] = None
	anexo_caminho: Optional[str] = None
