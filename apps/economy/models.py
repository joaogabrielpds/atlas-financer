# Modelos deste domínio serão implementados na próxima etapa.
from django.db import models


class EconomicIndicator(models.Model):

    code = models.CharField(max_length=50)
    name = models.CharField(max_length=150)
    category = models.CharField(max_length=100)
    country = models.CharField(max_length=100, default="Brasil")
    unit = models.CharField(max_length=30)

    value = models.DecimalField(
        max_digits=20,
        decimal_places=6
    )

    reference_date = models.DateField()
    published_at = models.DateTimeField(null=True, blank=True)
    source = models.CharField(max_length=100)

    collected_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-reference_date"]
        constraints = [
            models.UniqueConstraint(
                fields=["code", "reference_date", "source"],
                name="unique_indicator_reference_source"
            ),
        ]
        indexes = [
            models.Index(fields=["code", "-reference_date"]),
            models.Index(fields=["category"]),
        ]

    def __str__(self):
        return f"{self.name} - {self.reference_date}"