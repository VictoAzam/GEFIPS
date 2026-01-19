# Sistema de Autenticação - Finanças Pessoais

## 📋 Visão Geral

O aplicativo agora inclui um **sistema de autenticação seguro** com as seguintes características:

✅ **Senhas com hash bcrypt** (12 rounds)  
✅ **Login obrigatório** na inicialização do app  
✅ **Criação de novos usuários** com proteção por senha  
✅ **Seleção de perfil financeiro** após autenticação  
✅ **Isolamento de dados** por usuário e perfil  

---

## 🔐 Fluxo de Autenticação

### Primeira Execução (sem usuários)

1. **Tela de Login** aparece ao iniciar
2. **Clique na aba "Novo Usuário"**
3. Preencha os dados:
   - **Nome de usuário**: seu nome único (ex: "joao_silva")
   - **Email** (opcional): seu email
   - **Senha**: mínimo 6 caracteres
   - **Confirmar Senha**: deve ser idêntica

4. **Clique em "Criar Usuário"** → Usuário registrado com sucesso
5. **Volte para a aba "Login"**
6. **Faça login** com seu nome de usuário e senha
7. **Selecione ou crie um Perfil Financeiro**
8. **Acesse o aplicativo**

### Próximas Execuções (usuários existentes)

1. **Tela de Login** aparece
2. **Digite seu nome de usuário e senha**
3. **Clique em "Entrar"**
4. **Selecione um Perfil Financeiro**
5. **Acesse o aplicativo**

---

## 🛡️ Detalhes de Segurança

### Hash de Senha
- Algoritmo: **bcrypt** (padrão de segurança)
- Salt: **automático** (12 rounds)
- Verificação: **constant-time** (previne timing attacks)

### Armazenamento
- Senhas são **hashadas antes de armazenar**
- O banco de dados **nunca armazena senhas em plaintext**
- Campo `senha_hash` da tabela `usuarios` contém hash bcrypt

### Fluxo de Verificação
```
1. Usuário digita senha no login
   ↓
2. Sistema busca usuário por nome
   ↓
3. Sistema compara password + senha_hash com bcrypt.checkpw()
   ↓
4. Se match → Login bem-sucedido
   Se não → Mensagem de erro "Senha incorreta"
```

---

## 📂 Estrutura de Arquivos

### Novos Arquivos
```
ui/dialogs/login.py          ← Dialog de login/novo usuário (NEW)
utils/auth.py                ← Funções hash_password() e verify_password() (NEW)
```

### Arquivos Modificados
```
database/models_user.py       ← User agora tem campo senha_hash
database/db_manager.py        ← Métodos CRUD atualizados + get_user_by_name()
ui/main_window.py             ← Aceita current_user_id como parâmetro
ui/dialogs/user_profile.py    ← Compatível com login pre-autenticado
main.py                       ← Mostra LoginDialog antes de MainWindow
```

---

## 🔄 Mudanças na Inicialização

### Antes (sem autenticação)
```
main.py
  ↓
MainWindow.__init__()
  ↓
UserProfileDialog (seleciona usuário + perfil)
  ↓
App acessível
```

### Depois (com autenticação)
```
main.py
  ↓
LoginDialog (login ou novo usuário)
  ↓
MainWindow.__init__(current_user_id=...)
  ↓
UserProfileDialog (seleciona apenas perfil - usuário já autenticado)
  ↓
App acessível
```

---

## 📝 Variáveis de Ambiente (Opcional)

Atualmente, não há configuração de variáveis de ambiente para autenticação. Todas as credenciais são gerenciadas via banco de dados SQLite local.

---

## ✨ Funcionalidades Futuras Potenciais

- [ ] Sistema de recuperação de senha
- [ ] Mudança de senha após primeiro login
- [ ] Bloqueio de conta após N tentativas falhadas
- [ ] Logout e troca de usuário no menu
- [ ] Auditoria de login (log com timestamp)

---

## 🐛 Troubleshooting

### "Usuário não encontrado"
- Verifique se o nome de usuário está correto (case-sensitive)
- Crie um novo usuário se não tiver nenhum

### "Senha incorreta"
- Verifique se o Caps Lock está desativado
- Certifique-se de que confirmou a senha ao criar a conta

### Aplicativo não inicia
- Verifique se `bcrypt` está instalado: `pip install bcrypt`
- Execute o teste: `python test_auth_flow.py`

---

## 🧪 Teste de Autenticação

Um script de teste automatizado está disponível:

```bash
python test_auth_flow.py
```

Ele valida:
- ✓ Criação de usuário
- ✓ Hash de senha
- ✓ Busca de usuário por nome
- ✓ Verificação de senha correta/incorreta
- ✓ Criação de perfil financeiro
- ✓ Fluxo completo de autenticação

---

## 📚 Referências Técnicas

### Função de Hash
```python
from utils.auth import hash_password

password_hash = hash_password("minha_senha")
# Retorna: bcrypt hash com 12 rounds + salt
```

### Função de Verificação
```python
from utils.auth import verify_password

is_valid = verify_password("senha_digitada", password_hash)
# Retorna: True se correto, False se incorreto
```

### Busca de Usuário
```python
from database.db_manager import DbManager

db = DbManager("caminho/para/banco.db")
user = db.get_user_by_name("joao_silva")
# Retorna: User object ou None
```

---

**Versão**: 1.0  
**Data**: 2024  
**Status**: ✅ Em produção
