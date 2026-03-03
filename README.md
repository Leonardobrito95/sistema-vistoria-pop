Sistema de Controle de Vistorias e Manutenção de Infraestrutura (Vistoria POP)

Este é um sistema web desenvolvido em Python (Flask) e integrado ao banco de dados PostgreSQL. O objetivo principal é gerenciar vistorias técnicas, controlar manutenções preventivas e monitorar pendências em POPs (Point of Presence) de infraestrutura e telecomunicações.

<<<<<<< HEAD
Funcionalidades Principais
Dashboard Interativo: Visão geral em tempo real com farol de status (Verde para OK, Amarelo para Atenção e Vermelho para Vencido) para o acompanhamento das manutenções.

Formulários de Vistoria: Checklists completos abrangendo banco de baterias, geradores, ar-condicionado, rede elétrica, retificadoras e limpeza.

Validação de Imagens: Upload obrigatório de 3 a 6 fotos comprobatórias por vistoria, com validação de formato e limite de 10MB por arquivo.

Controle Automático de Vencimentos: Monitoramento de prazos implementado nativamente no sistema:

Banco de Baterias: 2 anos.
=======
---

## Funcionalidades Principais

- **Dashboard Interativo:** Visão geral em tempo real com farol de status (Verde para OK, Amarelo para Atenção e Vermelho para Vencido) para o acompanhamento das manutenções.
- **Formulários de Vistoria:** Checklists completos abrangendo banco de baterias, geradores, ar-condicionado, rede elétrica, retificadoras e limpeza.
- **Validação de Imagens:** Upload obrigatório de 3 a 6 fotos comprobatórias por vistoria, com validação de formato e limite de 10MB por arquivo.
- **Controle Automático de Vencimentos:** Monitoramento de prazos implementado nativamente no sistema:
  - **Banco de Baterias:** 2 anos.
  - **Gerador e Baterias de Gerador:** 6 meses.
  - **Ar-condicionado:** 3 meses.
  - **Limpeza e Teste de Bateria:** 30 dias.
- **Notificações por E-mail:** Alertas automáticos sobre atualizações de vistorias, vencimentos próximos e solução de pendências.
- **Controle de Acesso:** Divisão em 3 níveis (Administrador, Supervisor e Usuário Comum), garantindo segurança e permissões adequadas para cada perfil de uso.

## Tecnologias Utilizadas

- **Backend:** Python com framework Flask
- **Autenticação:** `Flask-Login` e `Werkzeug Security`
- **Banco de Dados:** PostgreSQL (via `psycopg2`)
- **Configurações:** `python-dotenv` para variáveis de ambiente
- **E-mail:** `smtplib` e `email.mime`
- **Uploads:** `secure_filename` do Werkzeug

---

## Estrutura do Projeto
>>>>>>> 95fbf8f (docs: Adiciona README.md detalhado com análise do projeto)

Gerador e Baterias de Gerador: 6 meses.

Ar-condicionado: 3 meses.

Limpeza e Teste de Bateria: 30 dias.

Notificações por E-mail: Alertas automáticos sobre atualizações de vistorias, vencimentos próximos e solução de pendências.

Controle de Acesso: Divisão em 3 níveis (Administrador, Supervisor e Usuário Comum), garantindo segurança e permissões adequadas para cada perfil de uso.

Tecnologias Utilizadas
Backend: Python com framework Flask

Autenticação: Flask-Login e Werkzeug Security

Banco de Dados: PostgreSQL (via psycopg2)

Configurações: python-dotenv para variáveis de ambiente

E-mail: smtplib e email.mime

Uploads: secure_filename do Werkzeug

Estrutura do Projeto
Plaintext
sistema-vistoria-pop/
├── .env.example            # Template de variáveis de ambiente
├── .gitignore              # Arquivos ignorados pelo Git
├── run.py                  # Ponto de entrada da aplicação
├── requirements.txt        # Dependências do projeto
├── ENTREGA_DO_SISTEMA.md   # Documentação de entrega e regras de negócio
├── app/                    # Aplicação principal
│   ├── __init__.py         # Rotas e controladores
│   ├── database.py         # Conexão e manipulação do banco de dados
│   ├── mailer.py           # Serviço de envio de e-mails via Locaweb SMTPLW
│   ├── static/             # Assets (CSS, JS, Imagens)
│   └── templates/          # Views em HTML e Jinja2
└── data/                   # Scripts SQL e diretório para armazenamento de uploads
<<<<<<< HEAD
Configuração e Execução
Pré-requisitos
Python 3.8 ou superior

Servidor PostgreSQL configurado e rodando

Passos para Instalação
1. Clone o repositório:

Bash
=======
```

---

## Configuração e Execução

### Pré-requisitos
- **Python 3.8** ou superior
- Servidor **PostgreSQL** configurado e rodando

### Passos para Instalação

**1. Clone o repositório:**
```bash
>>>>>>> 95fbf8f (docs: Adiciona README.md detalhado com análise do projeto)
git clone https://github.com/Leozin-web/sistema-vistoria-POP.git
cd sistema-vistoria-POP

<<<<<<< HEAD
2. Crie e ative o ambiente virtual:

Bash
=======
**2. Crie e ative o ambiente virtual:**
```bash
>>>>>>> 95fbf8f (docs: Adiciona README.md detalhado com análise do projeto)
python -m venv venv

# Linux/macOS:
source venv/bin/activate

# Windows:
venv\Scripts\activate

3. Instale as dependências:

Bash
pip install -r requirements.txt

<<<<<<< HEAD
4. Configure as variáveis de ambiente:
=======
**4. Configure as variáveis de ambiente:**
Copie o arquivo `.env.example` para `.env` e ajuste as credenciais do seu banco de dados e chaves de segurança.
>>>>>>> 95fbf8f (docs: Adiciona README.md detalhado com análise do projeto)

Copie o arquivo .env.example para .env e ajuste as credenciais do seu banco de dados e chaves de segurança.

Snippet de código
SECRET_KEY=sua-chave-secreta-aqui
DB_HOST=172.31.29.10
DB_PORT=5432
DB_NAME=sistema_db
DB_USER=seu_usuario
DB_PASS=sua_senha
<<<<<<< HEAD
Nota: As configurações do serviço de e-mail (Locaweb) podem ser ajustadas no arquivo mailer.py ou mapeadas via variáveis adicionais no .env.

5. Inicialize o banco de dados:

A criação das tabelas ocorre automaticamente na primeira execução da aplicação, consumindo o arquivo data/schema.sql através do módulo database.py.

6. Inicie a aplicação:

Bash
python run.py
O sistema estará disponível no seu navegador através do endereço http://localhost:5002.

Licença
=======
```
> **Nota:** As configurações do serviço de e-mail (Locaweb) podem ser ajustadas no arquivo `mailer.py` ou mapeadas via variáveis adicionais no `.env`.

**5. Inicialize o banco de dados:**
A criação das tabelas ocorre automaticamente na primeira execução da aplicação, consumindo o arquivo `data/schema.sql` através do módulo `database.py`.

**6. Inicie a aplicação:**
```bash
python run.py
```
O sistema estará disponível no seu navegador através do endereço `http://localhost:5002`.

---

## Licença
>>>>>>> 95fbf8f (docs: Adiciona README.md detalhado com análise do projeto)
Desenvolvido para uso interno. Todos os direitos reservados.
