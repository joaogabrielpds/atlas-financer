from rest_framework import serializers
from .models import Asset


class AssetSerializer(serializers.ModelSerializer):
    market_name = serializers.CharField(
        source="market.name",
        read_only=True
    )

    class Meta:
        model = Asset
        fields = "__all__"