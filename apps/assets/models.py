# Modelos deste domínio serão implementados na próxima etapa.
from django.db import models


class Asset(models.Model):

    class AssetType(models.TextChoices):
        STOCK = "STOCK", "Ação"
        REIT = "REIT", "FII"
        ETF = "ETF", "ETF"
        INDEX = "INDEX", "Índice"
        CRYPTO = "CRYPTO", "Criptomoeda"
        CURRENCY = "CURRENCY", "Moeda"
        COMMODITY = "COMMODITY", "Commodity"

    market = models.ForeignKey(
        "markets.Market",
        on_delete=models.PROTECT,
        related_name="assets",
        null=True,
        blank=True
    )

    ticker = models.CharField(max_length=30)
    name = models.CharField(max_length=150)
    asset_type = models.CharField(
        max_length=20,
        choices=AssetType.choices
    )

    currency = models.CharField(max_length=10, default="BRL")
    sector = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["ticker"]
        constraints = [
            models.UniqueConstraint(
                fields=["market", "ticker"],
                name="unique_market_ticker"
            ),
        ]
        indexes = [
            models.Index(fields=["ticker"]),
            models.Index(fields=["asset_type"]),
        ]

    def __str__(self):
        return f"{self.ticker} - {self.name}"
    
    