# Atlas Finance — Frontend

Frontend independente em HTML, CSS e JavaScript puro.

## Requisitos
- Python 3 para servidor estático local (ou outra ferramenta equivalente)
- Navegador moderno
- Backend Django REST Framework (será conectado nas próximas etapas)

## Executar no Fedora

Na pasta `frontend`:

```bash
python3 -m http.server 5500
```

Abra http://127.0.0.1:5500

O backend Django permanece em outra janela:

```bash
cd ~/Documentos/atlas-finance
source .venv/bin/activate
python manage.py runserver 8000
```

## Estrutura

- `index.html`: dashboard inicial.
- `css/main.css`: tema terminal escuro e responsividade.
- `js/config.js`: endereço da API e endpoints.
- `js/api.js`: cliente HTTP com Fetch API.
- `js/charts.js`: funções de Plotly.js e Lightweight Charts.
- `js/dashboard.js`: relógio, navegação e estado da API.

## Bibliotecas de gráficos

Plotly.js e TradingView Lightweight Charts são carregadas por CDN. É necessária conexão com a internet para carregar essas bibliotecas. A interface e a navegação local funcionam sem elas.

## Integração com o backend

A URL-base está em `js/config.js`:
`http://127.0.0.1:8000/api/v1`

Os endpoints são contratos planejados. Eles ainda precisam ser implementados no Django. Quando a API for criada, configure CORS no backend para permitir a origem `http://127.0.0.1:5500`.

O endpoint de health esperado é `GET /api/v1/health/`.

## Segurança e dados

- Não há cotações simuladas.
- Não coloque senhas ou chaves privadas no JavaScript do navegador.
- A autenticação e autorização serão implementadas no backend.
