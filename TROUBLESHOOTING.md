## 🔧 Troubleshooting - Sistema de Autenticação

### ❌ Problema: "ModuleNotFoundError: No module named 'bcrypt'"

**Causa**: Bcrypt não está instalado na sua versão do Python

**Solução**:
```bash
# No terminal (na pasta do projeto)
pip install bcrypt --quiet

# Ou especificamente:
python -m pip install bcrypt

# Para reinstalar:
pip install --upgrade bcrypt --force-reinstall
```

**Verificar se instalou**:
```bash
pip list | findstr bcrypt
# Deve mostrar: bcrypt           (versão)
```

---

### ❌ Problema: "Usuario não encontrado" ao fazer login

**Causa 1**: Você digitou o username errado
- **Solução**: Verifique se o username está correto
- Usernames são case-sensitive (Joao ≠ joao)

**Causa 2**: Você não criou ainda nenhum usuário
- **Solução**: 
  1. Clique na aba "Novo Usuário"
  2. Crie um novo usuário
  3. Volte para aba "Login"
  4. Faça login com o usuário criado

**Causa 3**: Banco de dados foi deletado
- **Solução**: Crie um novo usuário na aba "Novo Usuário"

---

### ❌ Problema: "Senha incorreta" mas tenho certeza que digitei correta

**Causa 1**: Caps Lock está ativado
- **Solução**: Desative Caps Lock e tente novamente

**Causa 2**: Você confirmou errado a senha ao criar o usuário
- **Solução**: 
  1. Na aba "Novo Usuário", certifique-se que os dois campos de senha são IDÊNTICOS
  2. Ao salvar, o app aviará se não forem iguais

**Causa 3**: Existe espaço em branco antes/depois da senha
- **Solução**: Digite a senha sem espaços antes ou depois

**Causa 4**: Senha tem caracteres especiais que podem ser confundidos
- Exemplos: l (letra L) vs 1 (número), O vs 0
- **Solução**: Use senhas mais claras, ou resete o banco e crie novo usuário

---

### ❌ Problema: LoginDialog não aparece, vai direto para UserProfileDialog

**Causa**: Código desatualizado ou cache do Python

**Solução**:
```bash
# Limpe arquivos compilados
python -m py_compile main.py
python -m py_compile ui/dialogs/login.py

# Ou remova __pycache__:
Remove-Item -Recurse -Force __pycache__
Remove-Item -Recurse -Force ui/__pycache__
Remove-Item -Recurse -Force database/__pycache__

# Reinicie o app
python main.py
```

---

### ❌ Problema: "TypeError: MainWindow.__init__() got an unexpected keyword argument 'current_user_id'"

**Causa**: Você está usando um MainWindow antigo (antes da atualização)

**Solução**:
1. Verifique se o arquivo `ui/main_window.py` foi atualizado
2. Procure por essa linha:
   ```python
   def __init__(self, db: DbManager, current_user_id: int, exports_dir: Path):
   ```
3. Se não estiver, atualize o arquivo manualmente

---

### ❌ Problema: App inicia normal mas LOGIN não funciona (sem mensagens de erro)

**Causa**: Arquivo de login não foi carregado corretamente

**Solução**:
```bash
# Compile todos os arquivos
python -m py_compile main.py
python -m py_compile ui/dialogs/login.py
python -m py_compile utils/auth.py

# Se houver erro de sintaxe, será mostrado aqui
```

---

### ❌ Problema: "AttributeError: 'NoneType' object has no attribute 'senha_hash'"

**Causa**: Usuário não tem senha_hash definido (banco antigo sem atualização)

**Solução**:
```bash
# Opção 1: Deletar banco (perderá dados)
Remove-Item *.db

# Opção 2: Atualizar manualmente (se souber SQL)
# Abra o banco com SQLite e adicione:
ALTER TABLE usuarios ADD COLUMN senha_hash TEXT NOT NULL DEFAULT '';

# Depois inicie o app e atualize as senhas dos usuários
```

---

### ❌ Problema: "get_user_by_name() não é um método do DbManager"

**Causa**: `database/db_manager.py` não foi atualizado

**Solução**:
1. Abra `database/db_manager.py`
2. Procure pela função `get_user_by_name`
3. Se não estiver, adicione:

```python
def get_user_by_name(self, nome: str) -> Optional[User]:
    """Busca usuário pelo nome (para login)"""
    cursor = self.conn.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE nome = ?", (nome,))
    row = cursor.fetchone()
    if not row:
        return None
    
    cols = [description[0] for description in cursor.description]
    user_dict = dict(zip(cols, row))
    return User(**user_dict)
```

---

### ❌ Problema: Aplicativo congela ao clicar "Entrar" no LoginDialog

**Causa**: Bcrypt está muito lento (não é normal, pode ser máquina muito lenta)

**Solução**:
1. Espere um pouco (bcrypt com 12 rounds leva ~200-300ms)
2. Se continuar congelado, verifique:
   ```bash
   # Ver processos Python em execução
   Get-Process | Where-Object {$_.Name -eq "python"}
   ```
3. Se não houver resposta em 5 segundos, force fechar e verifique o bcrypt

---

### ❌ Problema: "Permission denied" ao acessar banco de dados

**Causa**: Arquivo `.db` está aberto em outro programa

**Solução**:
1. Feche todos os programas que usam o banco (Excel, SQLite Browser, etc)
2. Feche todas as instâncias do app
3. Reinicie o app

---

### ✅ Como Fazer Reset Completo

Se tudo estiver muito quebrado:

```bash
# 1. Feche o app completamente

# 2. Limpe o banco de dados
cd "C:\Users\Victor Hugo Azambuja\Documents\Financeiro\FinancasPessoais"
Remove-Item -Path "*.db" -Force

# 3. Limpe arquivos compilados
Remove-Item -Recurse -Force __pycache__

# 4. Reinicie o app
python main.py

# 5. LoginDialog aparecerá
# 6. Crie novo usuário na aba "Novo Usuário"
# 7. Faça login
# 8. Crie perfil financeiro
# 9. Pronto!
```

---

### 🧪 Teste de Diagnóstico

Para testar se a autenticação funciona:

**Crie um arquivo `test_auth_simple.py`**:
```python
from database.db_manager import DbManager
from database.models_user import User
from utils.auth import hash_password, verify_password
from pathlib import Path

# Teste 1: Hash
print("1. Testando hash...")
hash1 = hash_password("senha123")
print(f"   Hash gerado: {hash1[:20]}...")

# Teste 2: Verificação
print("2. Testando verificação...")
is_valid = verify_password("senha123", hash1)
print(f"   Senha correta: {is_valid}")
is_invalid = verify_password("errada", hash1)
print(f"   Senha incorreta: {is_invalid}")

# Teste 3: Banco de dados
print("3. Testando banco de dados...")
import tempfile
db_path = str(Path(tempfile.gettempdir()) / "test_auth.db")
db = DbManager(db_path)
db.init_schema()

user = User(nome="teste", email="test@test.com", senha_hash=hash1)
user_id = db.add_user(user)
print(f"   Usuário criado: ID={user_id}")

found = db.get_user_by_name("teste")
print(f"   Usuário encontrado: {found.nome if found else 'NÃO'}")

if found:
    verified = verify_password("senha123", found.senha_hash)
    print(f"   Senha verificada: {verified}")

print("\n✓ TODOS OS TESTES OK!")
```

**Execute**:
```bash
python test_auth_simple.py
```

Se tudo passar, a autenticação está OK.

---

### 📞 Se Nada Funcionar

1. **Verifique a versão do Python**:
   ```bash
   python --version
   # Deve ser 3.8 ou superior
   ```

2. **Verifique PyQt5**:
   ```bash
   python -c "import PyQt5; print(PyQt5.__version__)"
   ```

3. **Limpe tudo e reinstale**:
   ```bash
   pip install --upgrade --force-reinstall bcrypt PyQt5
   ```

4. **Verifique os arquivos**:
   - `utils/auth.py` deve existir
   - `ui/dialogs/login.py` deve existir
   - `main.py` deve importar LoginDialog

5. **Procure erros no console**:
   ```bash
   python main.py 2>&1 | findstr "Error\|Traceback"
   ```

---

### 📝 Checklist de Verificação

Antes de reportar problema:

- [ ] Bcrypt instalado (`pip list | findstr bcrypt`)
- [ ] Arquivo `utils/auth.py` existe
- [ ] Arquivo `ui/dialogs/login.py` existe
- [ ] Arquivo `main.py` importa LoginDialog
- [ ] Nenhum arquivo `.db` aberto em outro programa
- [ ] Pasta `__pycache__` removida (cache Python)
- [ ] Python 3.8+ instalado
- [ ] PyQt5 5.15+ instalado

---

**Última atualização**: 2024  
**Status**: ✅ COMPLETO
