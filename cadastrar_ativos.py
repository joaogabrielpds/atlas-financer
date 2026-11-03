
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from apps.markets.models import Market
from apps.assets.models import Asset


# Criar mercado de índices, caso ainda não exista.
Market.objects.get_or_create(
    code="INDICES",
    defaults={
        "name": "Índices de Mercado",
        "country": "Global",
        "currency": "USD",
        "timezone": "UTC",
    },
)


assets = [
    # Ações brasileiras
    ("PETR4", "Petrobras PN", "STOCK", "BRL", "B3", "Petróleo e Gás"),
    ("VALE3", "Vale ON", "STOCK", "BRL", "B3", "Mineração"),
    ("ITUB4", "Itaú Unibanco PN", "STOCK", "BRL", "B3", "Financeiro"),
    ("BBAS3", "Banco do Brasil ON", "STOCK", "BRL", "B3", "Financeiro"),
    ("BBDC4", "Bradesco PN", "STOCK", "BRL", "B3", "Financeiro"),
    ("WEGE3", "WEG ON", "STOCK", "BRL", "B3", "Indústria"),

    # Fundos imobiliários
    ("MXRF11", "Maxi Renda", "REIT", "BRL", "B3", "FII"),
    ("BTLG11", "BTG Pactual Logística", "REIT", "BRL", "B3", "FII"),
    ("HGBS11", "Hedge Brasil Shopping", "REIT", "BRL", "B3", "FII"),
    ("GGRC11", "GGR Covepi Renda", "REIT", "BRL", "B3", "FII"),

    # ETFs
    ("IVVB11", "iShares S&P 500", "ETF", "BRL", "B3", "ETF"),

    # Ações americanas
    ("AAPL", "Apple Inc.", "STOCK", "USD", "NASDAQ", "Tecnologia"),
    ("MSFT", "Microsoft Corporation", "STOCK", "USD", "NASDAQ", "Tecnologia"),
    ("NVDA", "NVIDIA Corporation", "STOCK", "USD", "NASDAQ", "Semicondutores"),

    # Criptomoedas
    ("BTC-USD", "Bitcoin", "CRYPTO", "USD", "CRYPTO", "Criptomoedas"),
    ("ETH-USD", "Ethereum", "CRYPTO", "USD", "CRYPTO", "Criptomoedas"),
    ("SOL-USD", "Solana", "CRYPTO", "USD", "CRYPTO", "Criptomoedas"),

    # Índices
    ("IBOV", "Ibovespa", "INDEX", "BRL", "INDICES", "Índice brasileiro"),
    ("SP500", "S&P 500", "INDEX", "USD", "INDICES", "Índice americano"),
]


for ticker, name, asset_type, currency, market_code, sector in assets:
    market = Market.objects.get(code=market_code)

    asset, created = Asset.objects.get_or_create(
        market=market,
        ticker=ticker,
        defaults={
            "name": name,
            "asset_type": asset_type,
            "currency": currency,
            "sector": sector,
        },
    )

    status = "Criado" if created else "Já existia"
    print(f"{status}: {asset.ticker}")


print("\nCadastro finalizado!")
