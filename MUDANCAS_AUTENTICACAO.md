# Resumo das Mudanças - Sistema de Autenticação

## 🎯 Objetivo
Adicionar proteção por senha ao aplicativo de finanças pessoais, impedindo acesso não autorizado a outros usuários.

## ✅ O Que Foi Implementado

### 1. **Infraestrutura de Criptografia** (`utils/auth.py`)
```python
# Duas funções principais:
- hash_password(password: str) -> str
  • Criptografa senha com bcrypt (12 rounds)
  • Gera salt automaticamente
  
- verify_password(password: str, password_hash: str) -> bool
  • Verifica se senha corresponde ao hash
  • Verificação constant-time (segura contra timing attacks)
```

### 2. **Modelo de Usuário** (`database/models_user.py`)
```python
@dataclass
class User:
    id: Optional[int] = None
    nome: str = ""
    email: Optional[str] = None
    senha_hash: Optional[str] = None  # ← NOVO CAMPO
    data_criacao: Optional[date] = None
    ativo: bool = True
```

### 3. **Banco de Dados** (`database/db_manager.py`)
```python
# Schema atualizado (tabela usuarios)
CREATE TABLE usuarios (
    id INTEGER PRIMARY KEY,
    nome TEXT NOT NULL,
    email TEXT,
    senha_hash TEXT NOT NULL,  # ← NOVO
    data_criacao DATE,
    ativo BOOLEAN DEFAULT 1
);

# Métodos CRUD atualizados para lidar com senha_hash
- add_user(user: User) → armazena senha_hash
- get_user(user_id: int) → recupera senha_hash
- list_users() → recupera senha_hash
- update_user(user: User) → atualiza senha_hash

# Novo método para login
- get_user_by_name(nome: str) → User ou None
  Busca usuário por nome de usuário (necessário para login)
```

### 4. **Dialog de Login** (`ui/dialogs/login.py`)
```python
class LoginDialog(QDialog):
    # Duas abas:
    
    # ABA 1: LOGIN
    - Campo: Username (nome de usuário)
    - Campo: Password (senha com echo mascarado)
    - Botão: Entrar (valida credenciais)
    - Botão: Cancelar
    
    # ABA 2: NOVO USUÁRIO
    - Campo: Nome de usuário (único)
    - Campo: Email (opcional)
    - Campo: Senha (mín 6 caracteres)
    - Campo: Confirmar Senha
    - Botão: Criar Usuário (com validações)
    - Botão: Cancelar
    
    # Método público:
    get_authenticated_user_id() → int ou None
```

### 5. **Fluxo de Inicialização** (`main.py`)
```python
# Antes: MainWindow → UserProfileDialog
# Depois: LoginDialog → MainWindow → UserProfileDialog

def main():
    # ... inicializar config e banco ...
    
    # NOVO: Mostrar tela de login obrigatoriamente
    login_dialog = LoginDialog(None, db)
    if login_dialog.exec_() != LoginDialog.Accepted:
        return 0  # Usuário cancelou
    
    user_id = login_dialog.get_authenticated_user_id()
    if not user_id:
        return 1  # Falha na autenticação
    
    # NOVO parâmetro: current_user_id já autenticado
    win = MainWindow(db=db, current_user_id=user_id, exports_dir=...)
    win.show()
    
    return app.exec_()
```

### 6. **MainWindow Atualizada** (`ui/main_window.py`)
```python
class MainWindow(QMainWindow):
    def __init__(self, db: DbManager, current_user_id: int, exports_dir: Path):
        # NOVO parâmetro: current_user_id
        self.current_user_id = current_user_id
        
        # UserProfileDialog agora usa parâmetros:
        # - user_id: ID do usuário autenticado
        # - skip_user_selection=True: Pula seleção de usuário
        dlg = UserProfileDialog(
            self, 
            db, 
            user_id=current_user_id,
            skip_user_selection=True
        )
```

### 7. **UserProfileDialog Compatível** (`ui/dialogs/user_profile.py`)
```python
class UserProfileDialog(QDialog):
    def __init__(
        self, 
        parent, 
        db: DbManager,
        user_id: Optional[int] = None,  # NOVO
        skip_user_selection: bool = False  # NOVO
    ):
        # Se skip_user_selection=True:
        #   - Aba de usuários não é mostrada
        #   - Apenas aba de perfis financeiros
        #   - self.selected_user_id = user_id (pré-preenchido)
```

### 8. **Teste de Autenticação** (`test_auth_flow.py`)
```python
# Script independente que valida:
✓ Inicialização de banco
✓ Criação de usuário com senha
✓ Busca de usuário por nome
✓ Verificação de senha correta
✓ Rejeição de senha incorreta
✓ Criação de perfil financeiro
✓ Fluxo completo de autenticação

# Executar: python test_auth_flow.py
```

---

## 📊 Arquivos Alterados

| Arquivo | Tipo | Mudanças |
|---------|------|----------|
| `utils/auth.py` | ✨ NOVO | 2 funções: hash_password(), verify_password() |
| `ui/dialogs/login.py` | ✨ NOVO | LoginDialog completo com 2 abas |
| `database/models_user.py` | 🔧 MODIFICADO | +campo `senha_hash` no User |
| `database/db_manager.py` | 🔧 MODIFICADO | Schema atualizado, CRUD atualizado, +get_user_by_name() |
| `ui/main_window.py` | 🔧 MODIFICADO | +parâmetro `current_user_id` |
| `ui/dialogs/user_profile.py` | 🔧 MODIFICADO | +parâmetros `user_id` e `skip_user_selection` |
| `main.py` | 🔧 MODIFICADO | +LoginDialog antes de MainWindow |
| `test_auth_flow.py` | ✨ NOVO | Script de teste de autenticação |
| `AUTENTICACAO.md` | 📚 NOVO | Documentação de uso |

---

## 🔄 Comportamento Antes vs Depois

### ANTES
```
Iniciar app → UserProfileDialog
  ├── Seleciona usuário (fácil trocar)
  └── Seleciona perfil
→ App acesso sem proteção
```

**Problema:** Qualquer pessoa podia trocar de usuário facilmente!

### DEPOIS
```
Iniciar app → LoginDialog (obrigatório)
  ├── Login Tab:
  │   ├── Digite username e password
  │   └── Botão Entrar (valida credenciais)
  └── Novo Usuário Tab:
      ├── Nome, Email, Senha
      └── Botão Criar Usuário
↓ (apenas se login bem-sucedido)
MainWindow → UserProfileDialog
  ├── Seleciona perfil (usuário já autenticado)
  └── App acesso seguro
```

**Solução:** Senha obrigatória na inicialização!

---

## 🔐 Detalhes de Segurança

### Hash Bcrypt
- **Algoritmo**: bcrypt com 12 rounds
- **Salt**: Automático (gerado pelo bcrypt)
- **Complexidade**: O(2^12) = ~4000 iterações
- **Resistência**: Adequada para senhas pessoais

### Verificação de Senha
- Usa `bcrypt.checkpw()` (constant-time comparison)
- Previne timing attacks
- Mesmo hash correto e incorreto levam o mesmo tempo

### Armazenamento
- Senhas **nunca** são armazenadas em plaintext
- Apenas hash bcrypt é armazenado
- Impossível recuperar senha a partir do hash

---

## 🚀 Como Usar

### Primeira Vez
1. Inicie o app
2. LoginDialog aparece
3. Clique em "Novo Usuário"
4. Crie seu usuário com senha
5. Faça login
6. Crie um perfil financeiro
7. Use o app!

### Próximas Vezes
1. Inicie o app
2. LoginDialog aparece
3. Digite username e password
4. Selecione perfil
5. Use o app!

---

## ✨ Instalação de Dependências

Bcrypt já foi instalado. Para reinstalar (se necessário):
```bash
pip install bcrypt
```

---

## 🧪 Teste

Execute para validar tudo:
```bash
python test_auth_flow.py
```

Saída esperada:
```
✓ Banco criado
✓ Usuário criado
✓ Usuário encontrado
✓ Senha verificada
✓ Senha incorreta rejeitada
✓ Perfil criado
✓ Autenticação bem-sucedida
✓ Perfil listado
✓ TODOS OS TESTES PASSARAM!
```

---

## 📝 Status Final

✅ **Implementação Completa**
- ✅ Infraestrutura bcrypt funcional
- ✅ Login obrigatório implementado
- ✅ Criação de novos usuários com senha
- ✅ Integração com UI completa
- ✅ Testes passando
- ✅ Documentação gerada

**Próximas Features (futuro)**
- [ ] Logout e troca de usuário no menu
- [ ] Recuperação de senha
- [ ] Mudança de senha após primeiro login
- [ ] Bloqueio após tentativas falhadas
- [ ] Auditoria de login (logs)

---

## 📞 Suporte

Se encontrar problemas:
1. Execute `python test_auth_flow.py`
2. Verifique se bcrypt está instalado: `pip list | grep bcrypt`
3. Tente remover `*.db` e reiniciar (recria banco do zero)

**Última Atualização**: 2024
**Versão do App**: 1.0 + Sistema de Autenticação
