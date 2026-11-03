# Modelos deste domínio serão implementados na próxima etapa.
from django.db import models


class Market(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    country = models.CharField(max_length=100)
    currency = models.CharField(max_length=10, default="BRL")
    timezone = models.CharField(max_length=50, default="America/Sao_Paulo")
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Mercado"
        verbose_name_plural = "Mercados"

    def __str__(self):
        return f"{self.name} ({self.code})"


class Quote(models.Model):
    asset = models.ForeignKey(
        "assets.Asset",
        on_delete=models.CASCADE,
        related_name="quotes"
    )

    timestamp = models.DateTimeField()
    open = models.DecimalField(max_digits=20, decimal_places=6, null=True, blank=True)
    high = models.DecimalField(max_digits=20, decimal_places=6, null=True, blank=True)
    low = models.DecimalField(max_digits=20, decimal_places=6, null=True, blank=True)
    close = models.DecimalField(max_digits=20, decimal_places=6)
    adjusted_close = models.DecimalField(
        max_digits=20, decimal_places=6, null=True, blank=True
    )

    volume = models.BigIntegerField(null=True, blank=True)
    currency = models.CharField(max_length=10, default="BRL")
    source = models.CharField(max_length=50)
    collected_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-timestamp"]
        constraints = [
            models.UniqueConstraint(
                fields=["asset", "timestamp", "source"],
                name="unique_asset_quote_source"
            ),
            models.CheckConstraint(
                condition=models.Q(close__gt=0),
                name="quote_close_positive"
            ),
        ]
        indexes = [
            models.Index(fields=["asset", "-timestamp"]),
        ]

    def __str__(self):
        return f"{self.asset.ticker} - {self.timestamp}"