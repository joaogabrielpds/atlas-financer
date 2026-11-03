
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Market, Quote
from .serializers import MarketSerializer, QuoteSerializer


class MarketViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Market.objects.all()
    serializer_class = MarketSerializer


class QuoteViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = QuoteSerializer

    def get_queryset(self):
        queryset = Quote.objects.select_related("asset").all()

        ticker = self.request.query_params.get("ticker")

        if ticker:
            queryset = queryset.filter(
                asset__ticker__iexact=ticker
            )

        return queryset.order_by("timestamp")

    @action(detail=False, methods=["get"])
    def latest(self, request):
        from django.db.models import Max

        latest_quotes = Quote.objects.values(
            "asset__ticker"
        ).annotate(
            latest_date=Max("timestamp")
        )

        results = []

        for item in latest_quotes:
            quote = Quote.objects.select_related("asset").filter(
                asset__ticker=item["asset__ticker"],
                timestamp=item["latest_date"]
            ).first()

            if quote:
                results.append(QuoteSerializer(quote).data)

        return Response(results)
