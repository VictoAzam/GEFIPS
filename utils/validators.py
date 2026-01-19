from __future__ import annotations


def require_non_empty(text: str, field: str) -> str:
	if not text or not text.strip():
		raise ValueError(f"Campo obrigatório: {field}")
	return text.strip()


def require_positive(value: float, field: str) -> float:
	if value <= 0:
		raise ValueError(f"{field} deve ser maior que zero")
	return float(value)
