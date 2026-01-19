from __future__ import annotations


def format_brl(value: float) -> str:
	s = f"{value:,.2f}"
	s = s.replace(",", "X").replace(".", ",").replace("X", ".")
	return f"R$ {s}"
