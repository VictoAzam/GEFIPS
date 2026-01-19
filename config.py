from __future__ import annotations

import logging
import os
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class AppPaths:
	base_dir: Path
	data_dir: Path
	db_path: Path
	backup_dir: Path
	exports_dir: Path
	log_path: Path


def get_paths() -> AppPaths:
	# Usar pasta de dados do usuário (evita problemas de permissão em Program Files)
	user_base = Path(os.getenv("LOCALAPPDATA", Path.home())) / "GEFIPS"

	# Se estiver empacotado (PyInstaller), ignore o local do executável
	# e use sempre a pasta do usuário; em modo dev, usa a pasta do projeto.
	if getattr(sys, "frozen", False):
		base_dir = user_base
	else:
		base_dir = Path(__file__).resolve().parent

	data_dir = base_dir / "data"
	return AppPaths(
		base_dir=base_dir,
		data_dir=data_dir,
		db_path=data_dir / "financas.db",
		backup_dir=data_dir / "backup",
		exports_dir=data_dir / "exports",
		log_path=data_dir / "app.log",
	)


def ensure_dirs(paths: AppPaths) -> None:
	paths.data_dir.mkdir(parents=True, exist_ok=True)
	paths.backup_dir.mkdir(parents=True, exist_ok=True)
	paths.exports_dir.mkdir(parents=True, exist_ok=True)


def setup_logging(paths: AppPaths) -> None:
	logging.basicConfig(
		filename=str(paths.log_path),
		level=logging.INFO,
		format="%(asctime)s - %(levelname)s - %(message)s",
	)
