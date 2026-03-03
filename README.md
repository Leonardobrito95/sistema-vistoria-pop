# Sistema de Controle de Vistorias e Manutenção de Infraestrutura (Vistoria POP)

Um sistema web completo desenvolvido em Python (Flask) integrado ao banco de dados PostgreSQL para gerenciamento de vistorias técnicas, controle de manutenções preventivas e monitoramento de pendências em POPs (Point of Presence) de telecomunicações/infraestrutura.

## 🚀 Funcionalidades Principais

- **Dashboard Interativo e Público:** Visão geral em tempo real com farol de status (Verde para OK, Amarelo para Atenção e Vermelho para Vencido) sobre as manutenções dos POPs.
- **Formulários de Vistoria:** Checklist completo englobando banco de baterias, geradores, ar condicionado, rede elétrica, retificadoras e limpeza.
- **Validação de Imagens:** Upload obrigatório e com validação inteligente de 3 a 6 fotos comprobatorias das vistorias (limite de 10MB/arquivo).
- **Controle Autônomo de Vencimentos:** Lógica implementada que monitora prazos automaticamente:
  - Banco de Baterias (Validada a cada 2 anos).
  - Gerador e Baterias de Gerador (6 meses).
  - Ar Condicionado (3 meses).
  - Limpeza e Teste de Bateria (30 dias).
- **Notificação e Alertas via E-mail:** Sistema proativo integrado ao envio de e-mails para relatar quando uma vistoria for atualizada, quando a manutenção estiver prestes a vencer ou quando pendências forem solucionadas.
- **Níveis de Acesso Dinâmicos:** Conta com a diferenciação em 3 níveis (Administrador, Supervisor e Usuário Comum) oferecendo desde poder total do sistema a apenas a submissão e checagem pública.

## 🛠️ Tecnologias Utilizadas

- **Backend:** Python + Flask
- **Autenticação e Segurança:** Flask-Login e Werkzeug Security
- **Banco de Dados:** PostgreSQL (`psycopg2`)
- **Váriáveis de Ambiente:** `python-dotenv`
- **Comunicação por Email:** `smtplib` e `email.mime` 
- **Upload de Arquivos:** Werkzeug secure_filename

## 📁 Estrutura do Repositório

```text
sistema-vistoria-pop/
├── .env.example            # Exemplo de configuração de variáveis de ambiente
├── .gitignore              # Arquivos e diretórios não versionados
├── run.py                  # Arquivo de inicialização primária da aplicação
├── requirements.txt        # Lista restrita de dependências Python
├── ENTREGA_DO_SISTEMA.md   # Documentação de entrega e regras de negócios
├── app/                    # Pacote principal da aplicação web (Flask)
│   ├── __init__.py         # Rotas e controladores vitais web
│   ├── database.py         # Camada comunicadora do PostgreSQL Backend
│   ├── mailer.py           # Sistema autônomo de envio de E-mails/Alertas (Locaweb SMTPLW)
│   ├── static/             # Arquivos CSS, Javascript, Imagens, etc
│   └── templates/          # Arquivos e templates formatados em HTML e Jinja2
└── data/                   # Pasta para scripts SQL e salvamento dos uploads físicos de imagem
```

## ⚙️ Configuração e Execução

### Pré-requisitos
- **Python 3.8+**
- **Servidor PostgreSQL**

### Instruções

**1. Clone o repositório:**
```bash
git clone https://github.com/Leozin-web/sistema-vistoria-POP.git
cd sistema-vistoria-POP
```

**2. Crie e ative um ambiente virtual:**
```bash
python -m venv venv
# No Linux/Mac:
source venv/bin/activate
# No Windows:
venv\Scripts\activate
```

**3. Instale as dependências:**
```bash
pip install -r requirements.txt
```

**4. Variáveis de Ambiente:**
Copie o arquivo `.env.example` para `.env` e preencha com as suas configurações de Banco de dados e Chaves de Sessão.

```env
SECRET_KEY=sua-chave-secreta-aqui
DB_HOST=172.31.29.10
DB_PORT=5432
DB_NAME=sistema_db
DB_USER=seu_usuario
DB_PASS=sua_senha
```
*Note que se houver envios de e-mails, variáveis para Locaweb podem ser configuradas atrávez de instâncias de `mailer.py` ou via mais variáveis de ambiente.*

**5. Inicialize o Banco de Dados:**
A aplicação possui inicialização embutida em sua execução primária baseada no arquivo `data/schema.sql` através de requisição em `database.py`.

**6. Rode a aplicação localmente:**
```bash
python run.py
```
Acesse no seu navegador a aplicação via `http://localhost:5002`.

## 📜 Licença

Desenvolvido para uso interno. Todos os direitos reservados.
