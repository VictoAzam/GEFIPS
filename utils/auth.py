"""Autenticação e hash de senhas"""
import bcrypt


def hash_password(password: str) -> str:
	"""Hash uma senha com bcrypt"""
	if not password:
		raise ValueError("Senha não pode ser vazia")
	salt = bcrypt.gensalt(rounds=12)
	return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')


def verify_password(password: str, password_hash: str) -> bool:
	"""Verifica se a senha corresponde ao hash"""
	if not password or not password_hash:
		return False
	try:
		return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
	except Exception:
		return False
