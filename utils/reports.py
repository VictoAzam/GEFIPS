from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Any, Dict, List, Tuple

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import LongTable, Paragraph, SimpleDocTemplate, Spacer, TableStyle, Image

from database.db_manager import DbManager
from utils.formatters import format_brl


_MONTHS_SHORT = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"]


def generate_monthly_report_pdf(
	db: DbManager,
	exports_dir: Path,
	year: int,
	month: int,
) -> Path:
	exports_dir.mkdir(parents=True, exist_ok=True)
	month_label = _MONTHS_SHORT[month - 1]
	out = exports_dir / f"relatorio_{month_label}_{year}.pdf"

	entradas, saidas, saldo = db.get_month_balance(year, month)
	rows = db.list_month_transactions(year, month)

	doc = SimpleDocTemplate(str(out), pagesize=A4, title="Relatório mensal")
	styles = getSampleStyleSheet()

	story = []
	# Inserir logo no topo
	logo_path = Path(__file__).resolve().parent.parent / "logo" / "Gemini_Generated_Image_vwaqrtvwaqrtvwaq(1).png"
	if logo_path.exists():
		try:
			img = Image(str(logo_path))
			w, h = float(getattr(img, "imageWidth", 0) or 0), float(getattr(img, "imageHeight", 0) or 0)
			if w > 0 and h > 0:
				target_w = 120.0
				img.drawWidth = target_w
				img.drawHeight = target_w * (h / w)
			story.append(img)
			story.append(Spacer(1, 8))
		except Exception:
			pass
	story.append(Paragraph(f"Relatório mensal — {month_label.upper()}/{year}", styles["Title"]))
	story.append(Spacer(1, 10))
	story.append(Paragraph(f"Entradas: <b>{format_brl(entradas)}</b>", styles["Normal"]))
	story.append(Paragraph(f"Saídas: <b>{format_brl(saidas)}</b>", styles["Normal"]))
	story.append(Paragraph(f"Saldo: <b>{format_brl(saldo)}</b>", styles["Normal"]))
	story.append(Spacer(1, 12))

	table_data: List[List[str]] = [["Data", "Tipo", "Categoria", "Descrição", "Valor"]]
	for r in rows:
		data_txt = str(r.get("data") or "")
		tipo_txt = str(r.get("tipo") or "")
		cat_txt = str(r.get("categoria") or "")
		descr_txt = str(r.get("descricao") or "")
		valor = float(r.get("valor") or 0.0)
		table_data.append([data_txt, tipo_txt, cat_txt, descr_txt, format_brl(valor)])

	if len(table_data) == 1:
		story.append(Paragraph("Sem transações no período.", styles["Italic"]))
		doc.build(story)
		return out

	table = LongTable(
		table_data,
		repeatRows=1,
		colWidths=[70, 55, 120, 210, 70],
	)
	table.setStyle(
		TableStyle(
			[
				("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#F3F4F6")),
				("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#374151")),
				("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
				("FONTSIZE", (0, 0), (-1, 0), 9),
				("ALIGN", (-1, 1), (-1, -1), "RIGHT"),
				("VALIGN", (0, 0), (-1, -1), "TOP"),
				("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#E5E7EB")),
				("FONTSIZE", (0, 1), (-1, -1), 8),
			]
		)
	)
	story.append(table)

	doc.build(story)
	return out
