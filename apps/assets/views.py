# Views deste domínio serão implementadas conforme o escopo.
from rest_framework import viewsets

from .models import Asset
from .serializers import AssetSerializer


class AssetViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = AssetSerializer

    def get_queryset(self):
        queryset = Asset.objects.select_related("market").all()

        ticker = self.request.query_params.get("ticker")
        asset_type = self.request.query_params.get("type")

        if ticker:
            queryset = queryset.filter(ticker__icontains=ticker)

        if asset_type:
            queryset = queryset.filter(asset_type=asset_type.upper())

        return queryset