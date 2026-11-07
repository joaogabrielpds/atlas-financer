
from django.utils.dateparse import parse_date
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
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

        params = self.request.query_params

        # Filtro por ativo
        ticker = params.get("ticker")

        if ticker:
            queryset = queryset.filter(
                asset__ticker__iexact=ticker
            )

        # Filtro por data inicial
        start_date_param = params.get("start_date")

        if start_date_param:
            start_date = parse_date(start_date_param)

            if start_date is None:
                raise ValidationError({
                    "start_date": "Use o formato YYYY-MM-DD."
                })

            queryset = queryset.filter(
                timestamp__date__gte=start_date
            )

        # Filtro por data final
        end_date_param = params.get("end_date")

        if end_date_param:
            end_date = parse_date(end_date_param)

            if end_date is None:
                raise ValidationError({
                    "end_date": "Use o formato YYYY-MM-DD."
                })

            queryset = queryset.filter(
                timestamp__date__lte=end_date
            )

        # Validar intervalo
        if start_date_param and end_date_param:
            if start_date > end_date:
                raise ValidationError({
                    "date_range": "A data inicial não pode ser posterior à data final."
                })

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
