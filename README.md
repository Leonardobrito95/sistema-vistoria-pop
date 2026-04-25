# Sistema Vistoria POP

Sistema web para gestão de vistorias e manutenção preventiva de POPs (Pontos de Presença) de infraestrutura de rede.

## O problema que isso resolve

A equipe de infraestrutura vistoriava 8 POPs manualmente. Prazos de manutenção eram controlados em planilha, problemas encontrados ficavam em mensagens de WhatsApp e não havia rastreabilidade de quando cada item havia sido tratado.

Quando uma bateria vencia ou um gerador precisava de manutenção periódica, a equipe descobria tarde — ou não descobria.

## O que o sistema faz

Centraliza o registro de vistorias com formulário padronizado e upload de fotos. A partir de cada vistoria, o sistema gera pendências automaticamente para os itens com problema identificado e monitora os prazos de manutenção preventiva de cada POP.

Quando um prazo se aproxima do vencimento ou já venceu, o sistema dispara alertas por e-mail. Quando uma pendência é resolvida, o responsável registra a resolução e um e-mail de confirmação é enviado.

## POPs monitorados

8 locais de infraestrutura: Águas Claras, Taguatinga, Ceilândia, Arniqueiras, SIA, Vicente Pires, Sudoeste e Pátio Brasil.

## Ciclos de manutenção monitorados

| Equipamento | Periodicidade |
|---|---|
| Banco de baterias | 2 anos |
| Gerador | 6 meses |
| Bateria do gerador | 6 meses |
| Ar condicionado | 3 meses |
| Limpeza | 30 dias |
| Teste de bateria | 30 dias |

O dashboard exibe o status de cada item por POP com indicadores visuais: OK, Atenção (próximo do vencimento) ou Vencido.

## Stack

| Camada | Tecnologia |
|---|---|
| Backend | Python + Flask |
| Banco de dados | PostgreSQL |
| Autenticação | Flask-Login |
| Processo | systemd (produção) |

## Funcionalidades

- Formulário de vistoria com campos obrigatórios e upload de 3 a 6 fotos por POP
- Geração automática de pendências a partir dos itens problemáticos marcados na vistoria
- Dashboard com status de manutenção em tempo real para todos os POPs
- Alertas por e-mail para manutenções próximas do vencimento e vencidas
- Controle de pendências com registro de resolução e notificação por e-mail
- Histórico completo de vistorias com filtro por POP
- Gestão de usuários com três níveis de acesso: administrador, supervisor e inspetor
- Limpeza automática de registros com mais de 365 dias

## Estrutura de diretórios

```
sistema-vistoria-pop/
├── app/
│   ├── __init__.py        # Rotas e lógica da aplicação (Flask)
│   ├── database.py        # Acesso ao PostgreSQL (psycopg2)
│   ├── mailer.py          # Envio de alertas por e-mail
│   ├── static/            # CSS, JS e imagens
│   └── templates/         # HTML (dashboard, formulário, histórico, usuários)
├── data/
│   ├── schema.sql         # Schema do banco de dados
│   ├── schema_update.sql  # Migrations incrementais
│   └── uploads/           # Fotos de vistoria (ignorado no git)
├── .env.example
├── cleanup_db.py          # Script para limpeza manual de duplicatas
└── MANUAL_PRODUCAO.md     # Procedimentos de deploy e manutenção
```

## Configuração

### Variáveis de ambiente

Copie o `.env.example` e preencha:

```env
SECRET_KEY=sua_chave_secreta
DB_HOST=host_do_postgresql
DB_PORT=5432
DB_NAME=nome_do_banco
DB_USER=usuario
DB_PASS=senha
SMTP_SENDER_EMAIL=email_de_envio
```

### Banco de dados

```bash
# O schema é aplicado automaticamente na primeira execução.
# Para aplicar updates manualmente:
psql -U usuario -d nome_do_banco -f data/schema_update.sql
```

## Rodando localmente

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
flask run
```

## Rodando em produção (systemd)

```bash
# Status do serviço
sudo systemctl status sistema-vistoria

# Reiniciar após deploy
sudo systemctl restart sistema-vistoria

# Logs em tempo real
sudo journalctl -u sistema-vistoria -f
```
