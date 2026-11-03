# Atlas Finance

Plataforma pessoal de inteligência financeira para acompanhar mercados brasileiros e internacionais.

## Stack inicial
- Python 3.12+
- Django 5.2 LTS
- Django REST Framework
- PostgreSQL
- Pandas, NumPy e Plotly

## 1. Preparar ambiente no Fedora

```bash
sudo dnf install python3 python3-pip postgresql postgresql-server postgresql-contrib
mkdir -p ~/Projetos
cd ~/Projetos
unzip atlas-finance-starter.zip
cd atlas-finance

python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
cp .env.example .env
```

## 2. Configurar PostgreSQL

Inicialize o banco caso ainda não esteja inicializado:

```bash
sudo postgresql-setup --initdb
sudo systemctl enable --now postgresql
sudo -u postgres psql
```

No console do PostgreSQL:

```sql
CREATE USER atlas_user WITH PASSWORD 'sua_senha_forte';
CREATE DATABASE atlas_finance OWNER atlas_user;
\q
```

Edite o arquivo `.env` com a senha escolhida.

## 3. Inicializar Django

```bash
python manage.py check
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Acesse:
- Dashboard: http://127.0.0.1:8000/
- Administração: http://127.0.0.1:8000/admin/

## Estrutura

- `config/`: configurações e roteamento principal.
- `apps/dashboard/`: painel inicial.
- `apps/markets/`: mercados, índices e cotações.
- `apps/assets/`: cadastro de ativos.
- `apps/economy/`: indicadores macroeconômicos.
- `apps/fundamentals/`: fundamentos empresariais.
- `apps/technical/`: indicadores técnicos.
- `apps/news/`: notícias e eventos.
- `apps/portfolio/`: carteira e operações pessoais.
- `apps/intelligence/`: relatórios e interpretações.

## Decisões importantes
1. Dados externos devem entrar por adaptadores em `integrations/`.
2. Toda cotação deve registrar fonte e horário de referência/coleta.
3. Não tratar dados atrasados como cotações em tempo real.
4. Valores monetários devem usar `DecimalField` no banco, não `float`.
5. A plataforma é uma ferramenta de pesquisa; não promete previsão ou rentabilidade.

## Próxima entrega
Configurar os modelos de ativos, mercados, cotações e indicadores econômicos, incluindo testes e primeira integração de dados.
