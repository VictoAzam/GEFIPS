from __future__ import annotations

from datetime import date
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import LongTable, Paragraph, SimpleDocTemplate, Spacer, TableStyle, Image

from database.db_manager import DbManager
from utils.formatters import format_brl
from utils.investments import annual_rate_from_cdi, project_piggy


_MONTHS_SHORT = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"]


def generate_piggy_projection_report_pdf(
	db: DbManager,
	exports_dir: Path,
	piggy_id: int,
	horizon_months: int = 12,
) -> Path:
	exports_dir.mkdir(parents=True, exist_ok=True)

	row = db.get_piggy_bank(int(piggy_id))
	if not row:
		raise ValueError("Cofrinho não encontrado")

	nome = str(row.get("nome") or "")
	inst = str(row.get("instituicao") or "")
	percent_cdi = float(row.get("percent_cdi") or 0.0)
	cdi_aa = float(row.get("cdi_aa") or 0.0)
	principal = float(row.get("principal") or 0.0)
	aporte = float(row.get("aporte_mensal") or 0.0)
	inicio = date.fromisoformat(str(row.get("data_inicio")))
	aplicar = bool(row.get("aplicar_impostos"))

	annual = annual_rate_from_cdi(cdi_aa, percent_cdi)
	points = project_piggy(
		start=inicio,
		principal=principal,
		aporte_mensal=aporte,
		annual_rate=annual,
		horizon_months=int(horizon_months),
		aplicar_impostos=aplicar,
	)

	month_label = _MONTHS_SHORT[inicio.month - 1]
	out = exports_dir / f"cofrinho_{piggy_id}_{month_label}_{inicio.year}_proj_{horizon_months}m.pdf"

	doc = SimpleDocTemplate(str(out), pagesize=A4, title="Relatório de cofrinho")
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
	story.append(Paragraph(f"Cofrinho — {nome}", styles["Title"]))
	story.append(Paragraph(f"Instituição: <b>{inst}</b>", styles["Normal"]))
	story.append(
		Paragraph(
			f"Parâmetros: <b>{percent_cdi:.2f}%</b> do CDI | CDI <b>{cdi_aa:.2f}% a.a.</b> | Impostos: <b>{'sim' if aplicar else 'não'}</b>",
			styles["Normal"],
		)
	)
	story.append(Paragraph(f"Inicial: <b>{format_brl(principal)}</b> | Aporte mensal: <b>{format_brl(aporte)}</b>", styles["Normal"]))
	story.append(Spacer(1, 10))
	story.append(
		Paragraph(
			"Observação: projeção é uma aproximação (juros compostos mensais). IR/IOF são estimados como se houvesse resgate em cada mês.",
			styles["Italic"],
		)
	)
	story.append(Spacer(1, 12))

	table_data = [["Mês", "Aportes", "Bruto", "Rend.", "Impostos", "Líquido"]]
	for p in points:
		impostos = float(p.iof + p.ir)
		m = _MONTHS_SHORT[p.ref_date.month - 1]
		table_data.append(
			[
				f"{m}/{p.ref_date.year}",
				format_brl(float(p.total_aportes)),
				format_brl(float(p.saldo_bruto)),
				format_brl(float(p.rendimento_bruto)),
				format_brl(impostos),
				format_brl(float(p.saldo_liquido)),
			]
		)

	table = LongTable(table_data, repeatRows=1, colWidths=[70, 78, 78, 78, 78, 78])
	table.setStyle(
		TableStyle(
			[
				("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#F3F4F6")),
				("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#374151")),
				("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
				("FONTSIZE", (0, 0), (-1, 0), 9),
				("ALIGN", (1, 1), (-1, -1), "RIGHT"),
				("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#E5E7EB")),
				("FONTSIZE", (0, 1), (-1, -1), 8),
			]
		)
	)
	story.append(table)

	doc.build(story)
	return out
