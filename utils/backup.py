from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime, date
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from database.db_manager import DbManager
from database.models_user import FinancialProfile


BACKUP_VERSION = 1


def _iso_now() -> str:
	return datetime.utcnow().isoformat()


def export_profile(
	db: DbManager,
	backup_dir: Path,
	user_id: int,
	profile_id: int,
	filename: Optional[str] = None,
) -> Path:
	"""
	Exporta todos os dados do perfil financeiro especificado para um arquivo JSON em backup_dir.
	Retorna o caminho do arquivo gerado.
	"""
	backup_dir.mkdir(parents=True, exist_ok=True)

	# Coletar cabeçalhos e metadados
	user = db.get_user(user_id)
	profile = db.get_financial_profile(profile_id)
	if not user or not profile:
		raise ValueError("Usuário ou perfil inválido para backup")

	# Coletar dados das tabelas associadas ao perfil
	with db._connect() as conn:
		# Transações
		rows_tx = conn.execute(
			"""
			SELECT id, usuario_id, perfil_id, tipo, categoria, subcategoria, descricao, valor, data, pago, tags, anexo_caminho, data_registro
			FROM transacoes WHERE usuario_id = ? AND perfil_id = ? ORDER BY date(data) ASC, datetime(data_registro) ASC
			""",
			(user_id, profile_id),
		).fetchall()
		transactions: List[Dict[str, Any]] = [dict(r) for r in rows_tx]

		# Cofrinhos
		rows_piggy = conn.execute(
			"""
			SELECT id, usuario_id, perfil_id, nome, instituicao, percent_cdi, cdi_aa, principal, aporte_mensal, data_inicio, aplicar_impostos, created_at
			FROM cofrinhos WHERE usuario_id = ? AND perfil_id = ? ORDER BY datetime(created_at) ASC
			""",
			(user_id, profile_id),
		).fetchall()
		piggy_banks: List[Dict[str, Any]] = [dict(r) for r in rows_piggy]

		# Orçamentos
		rows_budgets = conn.execute(
			"""
			SELECT id, usuario_id, perfil_id, categoria, limite_mensal, mes, ano, ativo, descricao, data_criacao
			FROM orcamentos WHERE usuario_id = ? AND perfil_id = ? ORDER BY ano ASC, mes ASC, categoria ASC
			""",
			(user_id, profile_id),
		).fetchall()
		budgets: List[Dict[str, Any]] = [dict(r) for r in rows_budgets]

		# Metas
		rows_goals = conn.execute(
			"""
			SELECT id, usuario_id, perfil_id, nome, valor_alvo, valor_atual, data_inicio, data_alvo, ativo, descricao, prioridade, data_criacao
			FROM metas_financeiras WHERE usuario_id = ? AND perfil_id = ? ORDER BY date(data_alvo) ASC
			""",
			(user_id, profile_id),
		).fetchall()
		goals: List[Dict[str, Any]] = [dict(r) for r in rows_goals]

	data = {
		"version": BACKUP_VERSION,
		"exported_at": _iso_now(),
		"user": asdict(user),
		"profile": asdict(profile),
		"transactions": transactions,
		"piggy_banks": piggy_banks,
		"budgets": budgets,
		"goals": goals,
	}

	# Nome do arquivo
	if not filename:
		username = (user.nome or f"user{user_id}").replace(" ", "_")
		pname = (profile.nome or f"profile{profile_id}").replace(" ", "_")
		ts = datetime.now().strftime("%Y%m%d-%H%M%S")
		filename = f"backup_{username}_{pname}_{ts}.json"
	out_path = backup_dir / filename

	# Salvar JSON
	with out_path.open("w", encoding="utf-8") as f:
		json.dump(data, f, ensure_ascii=False, indent=2)
	return out_path


def restore_profile(
	db: DbManager,
	backup_file: Path,
	target_user_id: int,
	new_profile_name_suffix: Optional[str] = None,
) -> int:
	"""
	Restaura um backup JSON criando um novo perfil para o usuário-alvo e inserindo
	todos os registros associados. Retorna o novo profile_id.
	Não altera nem remove dados existentes.
	"""
	if not backup_file.exists():
		raise FileNotFoundError(str(backup_file))

	with backup_file.open("r", encoding="utf-8") as f:
		payload = json.load(f)

	# Validação básica
	if not isinstance(payload, dict) or "version" not in payload:
		raise ValueError("Arquivo de backup inválido")
	if int(payload.get("version", 0)) != BACKUP_VERSION:
		raise ValueError("Versão de backup incompatível")

	src_profile = payload.get("profile") or {}
	src_user = payload.get("user") or {}

	# Preparar novo perfil para o usuário alvo
	base_name = str(src_profile.get("nome") or "Perfil Restaurado")
	if new_profile_name_suffix:
		new_name = f"{base_name} {new_profile_name_suffix}"
	else:
		new_name = f"{base_name} (Restaurado)"

	profile = FinancialProfile(
		id=None,
		user_id=int(target_user_id),
		nome=new_name,
		descricao=src_profile.get("descricao"),
		moeda=str(src_profile.get("moeda") or "BRL"),
		cdi_aa_padrao=float(src_profile.get("cdi_aa_padrao") or 10.0),
		ir_automatico=bool(src_profile.get("ir_automatico", True)),
		iof_automatico=bool(src_profile.get("iof_automatico", True)),
		ano_fiscal=int(src_profile.get("ano_fiscal") or datetime.now().year),
		data_criacao=None,
		ativo=True,
	)
	new_profile_id = db.add_financial_profile(profile)

	# Inserir dados
	transactions: List[Dict[str, Any]] = list(payload.get("transactions") or [])
	piggies: List[Dict[str, Any]] = list(payload.get("piggy_banks") or [])
	budgets: List[Dict[str, Any]] = list(payload.get("budgets") or [])
	goals: List[Dict[str, Any]] = list(payload.get("goals") or [])

	with db._connect() as conn:
		# Transações
		for row in transactions:
			conn.execute(
				"""
				INSERT INTO transacoes (usuario_id, perfil_id, tipo, categoria, subcategoria, descricao, valor, data, pago, tags, anexo_caminho)
				VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
				""",
				(
					int(target_user_id),
					int(new_profile_id),
					str(row.get("tipo")),
					str(row.get("categoria")),
					row.get("subcategoria"),
					row.get("descricao"),
					float(row.get("valor") or 0.0),
					str(row.get("data")),
					1 if bool(row.get("pago", True)) else 0,
					row.get("tags"),
					row.get("anexo_caminho"),
				),
			)

		# Cofrinhos
		for row in piggies:
			conn.execute(
				"""
				INSERT INTO cofrinhos (usuario_id, perfil_id, nome, instituicao, percent_cdi, cdi_aa, principal, aporte_mensal, data_inicio, aplicar_impostos)
				VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
				""",
				(
					int(target_user_id),
					int(new_profile_id),
					str(row.get("nome")),
					str(row.get("instituicao")),
					float(row.get("percent_cdi") or 0.0),
					float(row.get("cdi_aa") or 0.0),
					float(row.get("principal") or 0.0),
					float(row.get("aporte_mensal") or 0.0),
					str(row.get("data_inicio")),
					1 if bool(row.get("aplicar_impostos", False)) else 0,
				),
			)

		# Orçamentos
		for row in budgets:
			conn.execute(
				"""
				INSERT INTO orcamentos (usuario_id, perfil_id, categoria, limite_mensal, mes, ano, ativo, descricao)
				VALUES (?, ?, ?, ?, ?, ?, ?, ?)
				""",
				(
					int(target_user_id),
					int(new_profile_id),
					str(row.get("categoria")),
					float(row.get("limite_mensal") or 0.0),
					int(row.get("mes") or 1),
					int(row.get("ano") or datetime.now().year),
					1 if bool(row.get("ativo", True)) else 0,
					row.get("descricao"),
				),
			)

		# Metas
		for row in goals:
			conn.execute(
				"""
				INSERT INTO metas_financeiras (usuario_id, perfil_id, nome, valor_alvo, valor_atual, data_inicio, data_alvo, ativo, descricao, prioridade)
				VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
				""",
				(
					int(target_user_id),
					int(new_profile_id),
					str(row.get("nome")),
					float(row.get("valor_alvo") or 0.0),
					float(row.get("valor_atual") or 0.0),
					str(row.get("data_inicio")),
					str(row.get("data_alvo")),
					1 if bool(row.get("ativo", True)) else 0,
					row.get("descricao"),
					str(row.get("prioridade") or "media"),
				),
			)

		conn.commit()

	return int(new_profile_id)
