# Views deste domínio serão implementadas conforme o escopo.
from rest_framework import viewsets

from .models import EconomicIndicator
from .serializers import EconomicIndicatorSerializer


class EconomicIndicatorViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = EconomicIndicatorSerializer

    def get_queryset(self):
        queryset = EconomicIndicator.objects.all()

        code = self.request.query_params.get("code")
        category = self.request.query_params.get("category")

        if code:
            queryset = queryset.filter(code__iexact=code)

        if category:
            queryset = queryset.filter(category__iexact=category)

        return queryset