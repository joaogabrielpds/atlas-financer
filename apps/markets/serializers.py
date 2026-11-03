from rest_framework import serializers
from .models import Market, Quote


class MarketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Market
        fields = "__all__"


class QuoteSerializer(serializers.ModelSerializer):
    ticker = serializers.CharField(
        source="asset.ticker",
        read_only=True
    )

    class Meta:
        model = Quote
        fields = "__all__"