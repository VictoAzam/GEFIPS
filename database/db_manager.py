from __future__ import annotations

import sqlite3
from dataclasses import asdict
from datetime import date
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from database.models import Transaction
from database.models_investments import PiggyBank
from database.models_user import User, FinancialProfile
from database.models_budgets import Budget, Goal


class DbManager:
	def __init__(self, db_path: Path):
		self.db_path = str(db_path)
		self.current_user_id: Optional[int] = None
		self.current_profile_id: Optional[int] = None

	def _connect(self) -> sqlite3.Connection:
		conn = sqlite3.connect(self.db_path)
		conn.row_factory = sqlite3.Row
		conn.execute("PRAGMA foreign_keys = ON;")
		return conn

	def set_current_user(self, user_id: int) -> None:
		"""Define o usuário atual"""
		self.current_user_id = user_id
		self.current_profile_id = None

	def set_current_profile(self, profile_id: int) -> None:
		"""Define o perfil financeiro atual"""
		self.current_profile_id = profile_id

	def init_schema(self) -> None:
		with self._connect() as conn:
			# Criar tabelas base
			conn.execute("""
			CREATE TABLE IF NOT EXISTS usuarios (
				id INTEGER PRIMARY KEY AUTOINCREMENT,
				nome TEXT NOT NULL UNIQUE,
				email TEXT,
				senha_hash TEXT NOT NULL,
				data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
				ativo BOOLEAN DEFAULT 1
			);
			""")

			conn.execute("""
			CREATE TABLE IF NOT EXISTS perfis_financeiros (
				id INTEGER PRIMARY KEY AUTOINCREMENT,
				usuario_id INTEGER NOT NULL,
				nome TEXT NOT NULL,
				descricao TEXT,
				moeda TEXT DEFAULT 'BRL',
				cdi_aa_padrao REAL DEFAULT 10.0,
				ir_automatico BOOLEAN DEFAULT 1,
				iof_automatico BOOLEAN DEFAULT 1,
				ano_fiscal INTEGER DEFAULT 2024,
				data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
				ativo BOOLEAN DEFAULT 1,
				FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
				UNIQUE(usuario_id, nome)
			);
			""")

			conn.execute("""
			CREATE TABLE IF NOT EXISTS transacoes (
				id INTEGER PRIMARY KEY AUTOINCREMENT,
				usuario_id INTEGER NOT NULL,
				perfil_id INTEGER NOT NULL,
				tipo TEXT NOT NULL,
				categoria TEXT NOT NULL,
				subcategoria TEXT,
				descricao TEXT,
				valor REAL NOT NULL,
				data DATE NOT NULL,
				data_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
				recorrente BOOLEAN DEFAULT 0,
				recorrente_id INTEGER,
				pago BOOLEAN DEFAULT 1,
				notas TEXT,
				tags TEXT,
				anexo_caminho TEXT,
				FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
				FOREIGN KEY (perfil_id) REFERENCES perfis_financeiros(id) ON DELETE CASCADE
			);
			""")

		conn.execute("""
		CREATE TABLE IF NOT EXISTS cofrinhos (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			usuario_id INTEGER NOT NULL,
			perfil_id INTEGER NOT NULL,
			nome TEXT NOT NULL,
			instituicao TEXT NOT NULL,
			percent_cdi REAL NOT NULL,
			cdi_aa REAL NOT NULL,
			principal REAL NOT NULL,
			aporte_mensal REAL DEFAULT 0,
			data_inicio DATE NOT NULL,
			aplicar_impostos BOOLEAN DEFAULT 0,
			created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
			FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
			FOREIGN KEY (perfil_id) REFERENCES perfis_financeiros(id) ON DELETE CASCADE
		);
		""")

		conn.execute("""
		CREATE TABLE IF NOT EXISTS orcamentos (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			usuario_id INTEGER NOT NULL,
			perfil_id INTEGER NOT NULL,
			categoria TEXT NOT NULL,
			limite_mensal REAL NOT NULL,
			mes INTEGER NOT NULL,
			ano INTEGER NOT NULL,
			ativo BOOLEAN DEFAULT 1,
			descricao TEXT,
			data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
			FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
			FOREIGN KEY (perfil_id) REFERENCES perfis_financeiros(id) ON DELETE CASCADE,
			UNIQUE(perfil_id, categoria, mes, ano)
		);
		""")

		conn.execute("""
		CREATE TABLE IF NOT EXISTS metas_financeiras (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			usuario_id INTEGER NOT NULL,
			perfil_id INTEGER NOT NULL,
			nome TEXT NOT NULL,
			valor_alvo REAL NOT NULL,
			valor_atual REAL DEFAULT 0,
			data_inicio DATE NOT NULL,
			data_alvo DATE NOT NULL,
			ativo BOOLEAN DEFAULT 1,
			descricao TEXT,
			prioridade TEXT DEFAULT 'media',
			data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
			FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
			FOREIGN KEY (perfil_id) REFERENCES perfis_financeiros(id) ON DELETE CASCADE
		);
		""")

		# Criar índices
		conn.execute("CREATE INDEX IF NOT EXISTS idx_transacoes_usuario ON transacoes(usuario_id);")
		conn.execute("CREATE INDEX IF NOT EXISTS idx_transacoes_perfil ON transacoes(perfil_id);")
		conn.execute("CREATE INDEX IF NOT EXISTS idx_transacoes_data ON transacoes(data);")
		conn.execute("CREATE INDEX IF NOT EXISTS idx_transacoes_tipo ON transacoes(tipo);")
		conn.execute("CREATE INDEX IF NOT EXISTS idx_cofrinhos_usuario ON cofrinhos(usuario_id);")
		conn.execute("CREATE INDEX IF NOT EXISTS idx_cofrinhos_perfil ON cofrinhos(perfil_id);")
		conn.execute("CREATE INDEX IF NOT EXISTS idx_orcamentos_perfil ON orcamentos(perfil_id);")
		conn.execute("CREATE INDEX IF NOT EXISTS idx_orcamentos_categoria ON orcamentos(categoria);")
		conn.execute("CREATE INDEX IF NOT EXISTS idx_metas_perfil ON metas_financeiras(perfil_id);")
		conn.execute("CREATE INDEX IF NOT EXISTS idx_metas_ativo ON metas_financeiras(ativo);")

		conn.commit()

	def add_transaction(self, tx: Transaction) -> int:
		if not self.current_user_id or not self.current_profile_id:
			raise ValueError("Usuário e perfil financeiro devem estar selecionados")

		payload = asdict(tx)
		payload.pop("id", None)

		sql = """
		INSERT INTO transacoes (usuario_id, perfil_id, tipo, categoria, subcategoria, descricao, valor, data, pago, tags, anexo_caminho)
		VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
		"""
		with self._connect() as conn:
			cur = conn.execute(
				sql,
				(
					self.current_user_id,
					self.current_profile_id,
					payload["tipo"],
					payload["categoria"],
					payload["subcategoria"],
					payload["descricao"],
					float(payload["valor"]),
					payload["data"].isoformat(),
					1 if payload.get("pago", True) else 0,
					payload.get("tags_json"),
					payload.get("anexo_caminho"),
				),
			)
			conn.commit()
			return int(cur.lastrowid)
			return int(cur.lastrowid)

	def list_last_transactions(self, limit: int = 10) -> List[Dict[str, Any]]:
		sql = """
		SELECT id, tipo, categoria, descricao, valor, data, pago
		FROM transacoes
		ORDER BY date(data) DESC, datetime(data_registro) DESC
		LIMIT ?
		"""
		with self._connect() as conn:
			rows = conn.execute(sql, (limit,)).fetchall()
			return [dict(r) for r in rows]

	def list_month_transactions(self, year: int, month: int) -> List[Dict[str, Any]]:
		if not self.current_user_id or not self.current_profile_id:
			return []
		start = date(year, month, 1)
		end = date(year + 1, 1, 1) if month == 12 else date(year, month + 1, 1)

		sql = """
		SELECT id, tipo, categoria, descricao, valor, data, pago
		FROM transacoes
		WHERE usuario_id = ? AND perfil_id = ? AND date(data) >= date(?) AND date(data) < date(?)
		ORDER BY date(data) DESC, datetime(data_registro) DESC
		"""
		with self._connect() as conn:
			rows = conn.execute(sql, (self.current_user_id, self.current_profile_id, start.isoformat(), end.isoformat())).fetchall()
			return [dict(r) for r in rows]

	def get_transaction(self, tx_id: int) -> Optional[Dict[str, Any]]:
		sql = """
		SELECT id, tipo, categoria, subcategoria, descricao, valor, data, pago, tags, anexo_caminho
		FROM transacoes
		WHERE id = ?
		"""
		with self._connect() as conn:
			row = conn.execute(sql, (int(tx_id),)).fetchone()
			return dict(row) if row else None

	def update_transaction(self, tx_id: int, tx: Transaction) -> None:
		sql = """
		UPDATE transacoes
		SET tipo = :tipo,
			categoria = :categoria,
			subcategoria = :subcategoria,
			descricao = :descricao,
			valor = :valor,
			data = :data,
			pago = :pago,
			tags = :tags,
			anexo_caminho = :anexo_caminho
		WHERE id = :id
		"""
		params = {
			"id": int(tx_id),
			"tipo": tx.tipo,
			"categoria": tx.categoria,
			"subcategoria": tx.subcategoria,
			"descricao": tx.descricao,
			"valor": float(tx.valor),
			"data": tx.data.isoformat(),
			"pago": 1 if tx.pago else 0,
			"tags": tx.tags_json,
			"anexo_caminho": tx.anexo_caminho,
		}
		with self._connect() as conn:
			conn.execute(sql, params)
			conn.commit()

	def delete_transaction(self, tx_id: int) -> None:
		with self._connect() as conn:
			conn.execute("DELETE FROM transacoes WHERE id = ?", (int(tx_id),))
			conn.commit()

	def list_piggy_banks(self) -> List[Dict[str, Any]]:
		if not self.current_user_id or not self.current_profile_id:
			return []
		
		sql = """
		SELECT id, nome, instituicao, percent_cdi, cdi_aa, principal, aporte_mensal, data_inicio, aplicar_impostos
		FROM cofrinhos
		WHERE usuario_id = ? AND perfil_id = ?
		ORDER BY datetime(created_at) DESC
		"""
		with self._connect() as conn:
			rows = conn.execute(sql, (self.current_user_id, self.current_profile_id)).fetchall()
			return [dict(r) for r in rows]

	def get_piggy_bank(self, piggy_id: int) -> Optional[Dict[str, Any]]:
		sql = """
		SELECT id, nome, instituicao, percent_cdi, cdi_aa, principal, aporte_mensal, data_inicio, aplicar_impostos
		FROM cofrinhos
		WHERE id = ? AND usuario_id = ?
		"""
		with self._connect() as conn:
			row = conn.execute(sql, (int(piggy_id), self.current_user_id)).fetchone()
			return dict(row) if row else None

	def add_piggy_bank(self, piggy: PiggyBank) -> int:
		if not self.current_user_id or not self.current_profile_id:
			raise ValueError("Usuário e perfil financeiro devem estar selecionados")
		
		sql = """
		INSERT INTO cofrinhos (usuario_id, perfil_id, nome, instituicao, percent_cdi, cdi_aa, principal, aporte_mensal, data_inicio, aplicar_impostos)
		VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
		"""
		with self._connect() as conn:
			cur = conn.execute(
				sql,
				(
					self.current_user_id,
					self.current_profile_id,
					piggy.nome,
					piggy.instituicao,
					float(piggy.percent_cdi),
					float(piggy.cdi_aa),
					float(piggy.principal),
					float(piggy.aporte_mensal),
					piggy.data_inicio.isoformat(),
					1 if piggy.aplicar_impostos else 0,
				),
			)
			conn.commit()
			return int(cur.lastrowid)

	def update_piggy_bank(self, piggy_id: int, piggy: PiggyBank) -> None:
		sql = """
		UPDATE cofrinhos
		SET nome = ?,
			instituicao = ?,
			percent_cdi = ?,
			cdi_aa = ?,
			principal = ?,
			aporte_mensal = ?,
			data_inicio = ?,
			aplicar_impostos = ?
		WHERE id = ? AND usuario_id = ?
		"""
		with self._connect() as conn:
			conn.execute(
				sql,
				(
					piggy.nome,
					piggy.instituicao,
					float(piggy.percent_cdi),
					float(piggy.cdi_aa),
					float(piggy.principal),
					float(piggy.aporte_mensal),
					piggy.data_inicio.isoformat(),
					1 if piggy.aplicar_impostos else 0,
					int(piggy_id),
					self.current_user_id,
				),
			)
			conn.commit()

	def delete_piggy_bank(self, piggy_id: int) -> None:
		with self._connect() as conn:
			conn.execute("DELETE FROM cofrinhos WHERE id = ? AND usuario_id = ?", (int(piggy_id), self.current_user_id))
			conn.commit()

	def get_month_balance(self, year: int, month: int) -> Tuple[float, float, float]:
		if not self.current_user_id or not self.current_profile_id:
			return 0.0, 0.0, 0.0
		start = date(year, month, 1)
		end = date(year + 1, 1, 1) if month == 12 else date(year, month + 1, 1)

		sql = """
		SELECT
			COALESCE(SUM(CASE WHEN tipo='entrada' THEN valor ELSE 0 END), 0) AS entradas,
			COALESCE(SUM(CASE WHEN tipo='saida' THEN valor ELSE 0 END), 0) AS saidas
		FROM transacoes
		WHERE usuario_id = ? AND perfil_id = ? AND date(data) >= date(?) AND date(data) < date(?) AND pago = 1
		"""
		with self._connect() as conn:
			row = conn.execute(sql, (self.current_user_id, self.current_profile_id, start.isoformat(), end.isoformat())).fetchone()
			entradas = float(row["entradas"])
			saidas = float(row["saidas"])
			return entradas, saidas, entradas - saidas

	def get_month_category_totals(self, year: int, month: int, tipo: str) -> List[Dict[str, Any]]:
		if not self.current_user_id or not self.current_profile_id:
			return []
		start = date(year, month, 1)
		end = date(year + 1, 1, 1) if month == 12 else date(year, month + 1, 1)

		sql = """
		SELECT categoria, COALESCE(SUM(valor), 0) AS total
		FROM transacoes
		WHERE usuario_id = ? AND perfil_id = ? AND date(data) >= date(?) AND date(data) < date(?) AND pago = 1 AND tipo = ?
		GROUP BY categoria
		ORDER BY total DESC
		"""
		with self._connect() as conn:
			rows = conn.execute(sql, (self.current_user_id, self.current_profile_id, start.isoformat(), end.isoformat(), str(tipo))).fetchall()
			return [dict(r) for r in rows]

	def get_month_daily_totals(self, year: int, month: int) -> List[Dict[str, Any]]:
		if not self.current_user_id or not self.current_profile_id:
			return []
		start = date(year, month, 1)
		end = date(year + 1, 1, 1) if month == 12 else date(year, month + 1, 1)

		sql = """
		SELECT date(data) AS dia,
			COALESCE(SUM(CASE WHEN tipo='entrada' THEN valor ELSE 0 END), 0) AS entradas,
			COALESCE(SUM(CASE WHEN tipo='saida' THEN valor ELSE 0 END), 0) AS saidas
		FROM transacoes
		WHERE usuario_id = ? AND perfil_id = ? AND date(data) >= date(?) AND date(data) < date(?) AND pago = 1
		GROUP BY date(data)
		ORDER BY date(data) ASC
		"""
		with self._connect() as conn:
			rows = conn.execute(sql, (self.current_user_id, self.current_profile_id, start.isoformat(), end.isoformat())).fetchall()
			return [dict(r) for r in rows]

	# ===== USUARIOS =====
	def add_user(self, user: User) -> int:
		sql = "INSERT INTO usuarios (nome, email, senha_hash, ativo) VALUES (?, ?, ?, ?)"
		with self._connect() as conn:
			cur = conn.execute(sql, (user.nome, user.email, user.senha_hash, 1 if user.ativo else 0))
			conn.commit()
			return int(cur.lastrowid)

	def get_user(self, user_id: int) -> Optional[User]:
		sql = "SELECT id, nome, email, senha_hash, data_criacao, ativo FROM usuarios WHERE id = ?"
		with self._connect() as conn:
			row = conn.execute(sql, (user_id,)).fetchone()
			if not row:
				return None
			return User(
				id=row["id"],
				nome=row["nome"],
				email=row["email"],
				senha_hash=row["senha_hash"],
				data_criacao=row["data_criacao"],
				ativo=bool(row["ativo"]),
			)

	def list_users(self) -> List[User]:
		sql = "SELECT id, nome, email, senha_hash, data_criacao, ativo FROM usuarios WHERE ativo = 1 ORDER BY nome"
		with self._connect() as conn:
			rows = conn.execute(sql).fetchall()
			return [
				User(
					id=row["id"],
					nome=row["nome"],
					email=row["email"],
					senha_hash=row["senha_hash"],
					data_criacao=row["data_criacao"],
					ativo=bool(row["ativo"]),
				)
				for row in rows
			]

	def update_user(self, user: User) -> None:
		sql = "UPDATE usuarios SET nome = ?, email = ?, senha_hash = ?, ativo = ? WHERE id = ?"
		with self._connect() as conn:
			conn.execute(sql, (user.nome, user.email, user.senha_hash, 1 if user.ativo else 0, user.id))
			conn.commit()

	def delete_user(self, user_id: int) -> None:
		with self._connect() as conn:
			conn.execute("DELETE FROM usuarios WHERE id = ?", (user_id,))
			conn.commit()

	def get_user_by_name(self, nome: str) -> Optional[User]:
		"""Busca usuário pelo nome"""
		sql = "SELECT id, nome, email, senha_hash, data_criacao, ativo FROM usuarios WHERE nome = ?"
		with self._connect() as conn:
			row = conn.execute(sql, (nome,)).fetchone()
			if not row:
				return None
			return User(
				id=row["id"],
				nome=row["nome"],
				email=row["email"],
				senha_hash=row["senha_hash"],
				data_criacao=row["data_criacao"],
				ativo=bool(row["ativo"]),
			)

	# ===== PERFIS FINANCEIROS =====
	def add_financial_profile(self, profile: FinancialProfile) -> int:
		sql = """
		INSERT INTO perfis_financeiros 
		(usuario_id, nome, descricao, moeda, cdi_aa_padrao, ir_automatico, iof_automatico, ano_fiscal, ativo)
		VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
		"""
		with self._connect() as conn:
			cur = conn.execute(
				sql,
				(
					profile.user_id,
					profile.nome,
					profile.descricao,
					profile.moeda,
					profile.cdi_aa_padrao,
					1 if profile.ir_automatico else 0,
					1 if profile.iof_automatico else 0,
					profile.ano_fiscal,
					1 if profile.ativo else 0,
				),
			)
			conn.commit()
			return int(cur.lastrowid)

	def get_financial_profile(self, profile_id: int) -> Optional[FinancialProfile]:
		sql = """
		SELECT id, usuario_id, nome, descricao, moeda, cdi_aa_padrao, ir_automatico, iof_automatico, ano_fiscal, data_criacao, ativo
		FROM perfis_financeiros WHERE id = ?
		"""
		with self._connect() as conn:
			row = conn.execute(sql, (profile_id,)).fetchone()
			if not row:
				return None
			return FinancialProfile(
				id=row["id"],
				user_id=row["usuario_id"],
				nome=row["nome"],
				descricao=row["descricao"],
				moeda=row["moeda"],
				cdi_aa_padrao=row["cdi_aa_padrao"],
				ir_automatico=bool(row["ir_automatico"]),
				iof_automatico=bool(row["iof_automatico"]),
				ano_fiscal=row["ano_fiscal"],
				data_criacao=row["data_criacao"],
				ativo=bool(row["ativo"]),
			)

	def list_user_financial_profiles(self, user_id: int) -> List[FinancialProfile]:
		sql = """
		SELECT id, usuario_id, nome, descricao, moeda, cdi_aa_padrao, ir_automatico, iof_automatico, ano_fiscal, data_criacao, ativo
		FROM perfis_financeiros WHERE usuario_id = ? AND ativo = 1 ORDER BY nome
		"""
		with self._connect() as conn:
			rows = conn.execute(sql, (user_id,)).fetchall()
			return [
				FinancialProfile(
					id=row["id"],
					user_id=row["usuario_id"],
					nome=row["nome"],
					descricao=row["descricao"],
					moeda=row["moeda"],
					cdi_aa_padrao=row["cdi_aa_padrao"],
					ir_automatico=bool(row["ir_automatico"]),
					iof_automatico=bool(row["iof_automatico"]),
					ano_fiscal=row["ano_fiscal"],
					data_criacao=row["data_criacao"],
					ativo=bool(row["ativo"]),
				)
				for row in rows
			]

	def update_financial_profile(self, profile: FinancialProfile) -> None:
		sql = """
		UPDATE perfis_financeiros 
		SET nome = ?, descricao = ?, moeda = ?, cdi_aa_padrao = ?, ir_automatico = ?, iof_automatico = ?, ano_fiscal = ?, ativo = ?
		WHERE id = ?
		"""
		with self._connect() as conn:
			conn.execute(
				sql,
				(
					profile.nome,
					profile.descricao,
					profile.moeda,
					profile.cdi_aa_padrao,
					1 if profile.ir_automatico else 0,
					1 if profile.iof_automatico else 0,
					profile.ano_fiscal,
					1 if profile.ativo else 0,
					profile.id,
				),
			)
			conn.commit()

	def delete_financial_profile(self, profile_id: int) -> None:
		with self._connect() as conn:
			conn.execute("DELETE FROM perfis_financeiros WHERE id = ?", (profile_id,))
			conn.commit()

	# ===== ORÇAMENTOS =====
	def add_budget(self, budget: Budget) -> int:
		"""Adiciona um novo orçamento"""
		if not self.current_user_id or not self.current_profile_id:
			raise ValueError("Usuário e perfil financeiro devem estar selecionados")
		
		sql = """
		INSERT INTO orcamentos (usuario_id, perfil_id, categoria, limite_mensal, mes, ano, ativo, descricao)
		VALUES (?, ?, ?, ?, ?, ?, ?, ?)
		"""
		with self._connect() as conn:
			cur = conn.execute(
				sql,
				(
					self.current_user_id,
					self.current_profile_id,
					budget.categoria,
					float(budget.limite_mensal),
					budget.mes,
					budget.ano,
					1 if budget.ativo else 0,
					budget.descricao,
				),
			)
			conn.commit()
			return int(cur.lastrowid)

	def get_budget(self, budget_id: int) -> Optional[Dict[str, Any]]:
		"""Obtém um orçamento específico"""
		sql = """
		SELECT id, categoria, limite_mensal, mes, ano, ativo, descricao
		FROM orcamentos WHERE id = ? AND usuario_id = ?
		"""
		with self._connect() as conn:
			row = conn.execute(sql, (budget_id, self.current_user_id)).fetchone()
			return dict(row) if row else None

	def list_budgets(self, ano: int, mes: int) -> List[Dict[str, Any]]:
		"""Lista orçamentos de um mês específico"""
		if not self.current_user_id or not self.current_profile_id:
			return []
		
		sql = """
		SELECT id, categoria, limite_mensal, mes, ano, ativo, descricao
		FROM orcamentos
		WHERE usuario_id = ? AND perfil_id = ? AND ano = ? AND mes = ? AND ativo = 1
		ORDER BY categoria
		"""
		with self._connect() as conn:
			rows = conn.execute(sql, (self.current_user_id, self.current_profile_id, ano, mes)).fetchall()
			return [dict(r) for r in rows]

	def update_budget(self, budget_id: int, budget: Budget) -> None:
		"""Atualiza um orçamento"""
		sql = """
		UPDATE orcamentos
		SET categoria = ?, limite_mensal = ?, ativo = ?, descricao = ?
		WHERE id = ? AND usuario_id = ?
		"""
		with self._connect() as conn:
			conn.execute(
				sql,
				(
					budget.categoria,
					float(budget.limite_mensal),
					1 if budget.ativo else 0,
					budget.descricao,
					budget_id,
					self.current_user_id,
				),
			)
			conn.commit()

	def delete_budget(self, budget_id: int) -> None:
		"""Deleta um orçamento"""
		with self._connect() as conn:
			conn.execute("DELETE FROM orcamentos WHERE id = ? AND usuario_id = ?", (budget_id, self.current_user_id))
			conn.commit()

	def get_budget_summary(self, ano: int, mes: int) -> List[Dict[str, Any]]:
		"""Retorna um resumo de cada orçamento com gastos atuais"""
		if not self.current_user_id or not self.current_profile_id:
			return []
		
		start = date(ano, mes, 1)
		end = date(ano + 1, 1, 1) if mes == 12 else date(ano, mes + 1, 1)
		
		sql = """
		SELECT 
			o.id,
			o.categoria,
			o.limite_mensal,
			COALESCE(SUM(t.valor), 0) AS gasto_atual,
			CASE WHEN COALESCE(SUM(t.valor), 0) > o.limite_mensal THEN 1 ELSE 0 END AS excedido
		FROM orcamentos o
		LEFT JOIN transacoes t ON 
			o.categoria = t.categoria AND 
			t.usuario_id = o.usuario_id AND
			t.perfil_id = o.perfil_id AND
			t.tipo = 'saida' AND
			t.pago = 1 AND
			date(t.data) >= date(?) AND
			date(t.data) < date(?)
		WHERE o.usuario_id = ? AND o.perfil_id = ? AND o.ano = ? AND o.mes = ? AND o.ativo = 1
		GROUP BY o.id, o.categoria, o.limite_mensal
		ORDER BY o.categoria
		"""
		with self._connect() as conn:
			rows = conn.execute(sql, (start.isoformat(), end.isoformat(), self.current_user_id, self.current_profile_id, ano, mes)).fetchall()
			return [dict(r) for r in rows]

	# ===== METAS FINANCEIRAS =====
	def add_goal(self, goal: Goal) -> int:
		"""Adiciona uma nova meta financeira"""
		if not self.current_user_id or not self.current_profile_id:
			raise ValueError("Usuário e perfil financeiro devem estar selecionados")
		
		sql = """
		INSERT INTO metas_financeiras (usuario_id, perfil_id, nome, valor_alvo, valor_atual, data_inicio, data_alvo, ativo, descricao, prioridade)
		VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
		"""
		with self._connect() as conn:
			cur = conn.execute(
				sql,
				(
					self.current_user_id,
					self.current_profile_id,
					goal.nome,
					float(goal.valor_alvo),
					float(goal.valor_atual),
					goal.data_inicio.isoformat(),
					goal.data_alvo.isoformat(),
					1 if goal.ativo else 0,
					goal.descricao,
					goal.prioridade,
				),
			)
			conn.commit()
			return int(cur.lastrowid)

	def get_goal(self, goal_id: int) -> Optional[Dict[str, Any]]:
		"""Obtém uma meta específica"""
		sql = """
		SELECT id, nome, valor_alvo, valor_atual, data_inicio, data_alvo, ativo, descricao, prioridade
		FROM metas_financeiras WHERE id = ? AND usuario_id = ?
		"""
		with self._connect() as conn:
			row = conn.execute(sql, (goal_id, self.current_user_id)).fetchone()
			return dict(row) if row else None

	def list_goals(self, ativas_apenas: bool = True) -> List[Dict[str, Any]]:
		"""Lista metas financeiras"""
		if not self.current_user_id or not self.current_profile_id:
			return []
		
		sql = """
		SELECT id, nome, valor_alvo, valor_atual, data_inicio, data_alvo, ativo, descricao, prioridade
		FROM metas_financeiras
		WHERE usuario_id = ? AND perfil_id = ?
		"""
		
		if ativas_apenas:
			sql += " AND ativo = 1"
		
		sql += " ORDER BY prioridade DESC, data_alvo ASC"
		
		with self._connect() as conn:
			rows = conn.execute(sql, (self.current_user_id, self.current_profile_id)).fetchall()
			return [dict(r) for r in rows]

	def update_goal(self, goal_id: int, goal: Goal) -> None:
		"""Atualiza uma meta financeira"""
		sql = """
		UPDATE metas_financeiras
		SET nome = ?, valor_alvo = ?, valor_atual = ?, data_inicio = ?, data_alvo = ?, ativo = ?, descricao = ?, prioridade = ?
		WHERE id = ? AND usuario_id = ?
		"""
		with self._connect() as conn:
			conn.execute(
				sql,
				(
					goal.nome,
					float(goal.valor_alvo),
					float(goal.valor_atual),
					goal.data_inicio.isoformat(),
					goal.data_alvo.isoformat(),
					1 if goal.ativo else 0,
					goal.descricao,
					goal.prioridade,
					goal_id,
					self.current_user_id,
				),
			)
			conn.commit()

	def delete_goal(self, goal_id: int) -> None:
		"""Deleta uma meta financeira"""
		with self._connect() as conn:
			conn.execute("DELETE FROM metas_financeiras WHERE id = ? AND usuario_id = ?", (goal_id, self.current_user_id))
			conn.commit()

	def get_goal_progress(self, goal_id: int) -> Optional[Dict[str, Any]]:
		"""Retorna o progresso de uma meta"""
		goal = self.get_goal(goal_id)
		if not goal:
			return None
		
		valor_alvo = float(goal["valor_alvo"])
		valor_atual = float(goal["valor_atual"])
		progresso = (valor_atual / valor_alvo * 100) if valor_alvo > 0 else 0
		
		return {
			**goal,
			"progresso_percentual": min(100, progresso),
			"faltam": max(0, valor_alvo - valor_atual),
		}
