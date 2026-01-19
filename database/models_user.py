from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Optional


@dataclass
class User:
	"""Perfil de usuário"""
	id: Optional[int] = None
	nome: str = ""
	email: Optional[str] = None
	senha_hash: Optional[str] = None  # bcrypt hash
	data_criacao: Optional[date] = None
	ativo: bool = True


@dataclass
class FinancialProfile:
	"""Perfil financeiro do usuário"""
	id: Optional[int] = None
	user_id: int = 0
	nome: str = ""
	descricao: Optional[str] = None
	moeda: str = "BRL"
	cdi_aa_padrao: float = 10.0  # CDI anual padrão em %
	ir_automatico: bool = True
	iof_automatico: bool = True
	ano_fiscal: int = 2024
	data_criacao: Optional[date] = None
	ativo: bool = True
