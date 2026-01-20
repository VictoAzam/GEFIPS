# 💰 GEFIPS - Gestor Financeira Pessoal Simpes

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![PyQt6](https://img.shields.io/badge/PyQt6-6.0+-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Platform](https://img.shields.io/badge/platform-Windows-lightgrey.svg)
![Release](https://img.shields.io/github/v/release/VictoAzam/GEFIPS)
![Downloads](https://img.shields.io/github/downloads/VictoAzam/GEFIPS/total)

Sistema completo de gestão financeira pessoal desenvolvido em Python com interface gráfica moderna.

## 📥 Download

**[⬇️ Baixar GEFIPS v1.0.0 (Windows)](https://github.com/VictoAzam/GEFIPS/releases/tag/v1.0.0)**

Faça o download do executável e comece a usar imediatamente, sem necessidade de instalar Python ou dependências!

## 📋 Sobre o Projeto

GEFIPS é um sistema desktop para controle financeiro pessoal que permite gerenciar receitas, despesas, investimentos, metas e cofrinhos virtuais. Com uma interface intuitiva e recursos avançados de relatórios e gráficos, torna o controle financeiro mais simples e eficiente.

## ✨ Funcionalidades

- 🔐 **Autenticação de Usuários** - Sistema completo de login e perfis
- 💸 **Controle de Transações** - Registro de receitas e despesas
- 📊 **Orçamentos** - Planejamento e acompanhamento de orçamentos mensais
- 🎯 **Metas Financeiras** - Defina e acompanhe suas metas
- 🐷 **Cofrinhos Virtuais** - Economize para objetivos específicos
- 💹 **Investimentos** - Acompanhamento de aplicações financeiras
- 📈 **Gráficos e Relatórios** - Visualizações detalhadas de suas finanças
- 💾 **Backup Automático** - Proteção dos seus dados
- 🎨 **Interface Moderna** - Design limpo e intuitivo

## 🚀 Instalação

### Pré-requisitos

- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)

### Passo a Passo

1. **Clone o repositório**
   ```bash
   git clone https://github.com/VictoAzam/GEFIPS.git
   cd GEFIPS
   ```

2. **Crie um ambiente virtual** (recomendado)
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   ```

3. **Instale as dependências**
   ```bash
   pip install -r requirements.txt
   ```

4. **Execute o programa**
   ```bash
   python main.py
   ```

## 📦 Dependências Principais

- **PyQt6** - Interface gráfica
- **SQLAlchemy** - Gerenciamento de banco de dados
- **Matplotlib** - Gráficos e visualizações
- **Pandas** - Análise de dados
- **Pillow** - Processamento de imagens
- **ReportLab** - Geração de PDFs

## 🏗️ Estrutura do Projeto

```
GEFIPS/
├── main.py              # Arquivo principal
├── config.py            # Configurações
├── requirements.txt     # Dependências
├── database/            # Modelos e gerenciamento do banco
├── ui/                  # Interfaces e diálogos
│   └── dialogs/         # Janelas de diálogo
├── utils/               # Utilitários e helpers
├── data/                # Dados e backups
├── fonts/               # Fontes customizadas
├── logo/                # Recursos visuais
└── docs/                # Documentação adicional

```

## 💻 Uso

1. **Primeiro Acesso**
   - Crie uma conta na tela de login
   - Configure seu perfil

2. **Adicionar Transações**
   - Use os botões "+" para adicionar receitas ou despesas
   - Categorize suas transações

3. **Criar Orçamentos**
   - Acesse a aba "Orçamentos"
   - Defina limites para suas categorias

4. **Acompanhar Investimentos**
   - Registre suas aplicações
   - Visualize o rendimento

5. **Gerar Relatórios**
   - Acesse a aba "Relatórios"
   - Exporte para PDF ou Excel

## 🔒 Segurança

- Senhas criptografadas com hash bcrypt
- Dados armazenados localmente em SQLite
- Backup automático configurável

## 🛠️ Compilação (Executável)

Para gerar um executável Windows:

```bash
pyinstaller GEFIPS.spec
```

O executável será gerado na pasta `dist/`.

## 📚 Documentação

Para documentação detalhada, consulte a pasta [`docs/`](docs/):

- [Guia Rápido](docs/GUIA_RAPIDO.md)
- [Autenticação](docs/AUTENTICACAO.md)
- [Novas Funcionalidades](docs/NOVAS_FUNCIONALIDADES.md)
- [Troubleshooting](docs/TROUBLESHOOTING.md)

## 🤝 Contribuindo

Contribuições são bem-vindas! Sinta-se à vontade para:

1. Fazer um Fork do projeto
2. Criar uma branch para sua feature (`git checkout -b feature/MinhaFeature`)
3. Commit suas mudanças (`git commit -m 'Adiciona MinhaFeature'`)
4. Push para a branch (`git push origin feature/MinhaFeature`)
5. Abrir um Pull Request

## 📝 Licença

Este projeto está sob a licença MIT. Veja o arquivo LICENSE para mais detalhes.

## 👤 Autor

**Victor Hugo Azambuja**

- GitHub: [@VictoAzam](https://github.com/VictoAzam)

## 🙏 Agradecimentos

- Comunidade Python
- Bibliotecas open-source utilizadas
- Todos que contribuíram com feedback

---

⭐ Se este projeto te ajudou, considere dar uma estrela!
