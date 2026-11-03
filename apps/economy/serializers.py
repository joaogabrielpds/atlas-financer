from rest_framework import serializers
from .models import EconomicIndicator


class EconomicIndicatorSerializer(serializers.ModelSerializer):
    class Meta:
        model = EconomicIndicator
        fields = "__all__"