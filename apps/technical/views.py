
from django.shortcuts import get_object_or_404
from django.utils.dateparse import parse_date

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError

from apps.assets.models import Asset
from apps.markets.models import Quote

from .services.indicators import calculate_indicators


class TechnicalIndicatorsView(APIView):

    def get(self, request, ticker):
        asset = get_object_or_404(
            Asset,
            ticker__iexact=ticker,
            is_active=True,
        )

        start_param = request.query_params.get("start_date")
        end_param = request.query_params.get("end_date")

        start_date = None
        end_date = None

        if start_param:
            start_date = parse_date(start_param)

            if start_date is None:
                raise ValidationError({
                    "start_date": "Use o formato YYYY-MM-DD."
                })

        if end_param:
            end_date = parse_date(end_param)

            if end_date is None:
                raise ValidationError({
                    "end_date": "Use o formato YYYY-MM-DD."
                })

        if start_date and end_date and start_date > end_date:
            raise ValidationError({
                "date_range": "Data inicial posterior à data final."
            })

        queryset = Quote.objects.filter(
            asset=asset
        ).order_by("timestamp")

        if end_date:
            queryset = queryset.filter(
                timestamp__date__lte=end_date
            )

        quotes = list(
            queryset.values("timestamp", "close")
        )

        data = calculate_indicators(quotes)

        if start_date:
            data = [
                item for item in data
                if item["timestamp"][:10] >= start_date.isoformat()
            ]

        return Response({
            "ticker": asset.ticker,
            "count": len(data),
            "indicators": [
                "SMA 20",
                "SMA 50",
                "SMA 200",
                "EMA 9",
                "EMA 21",
                "RSI 14",
                "MACD",
                "Bollinger Bands",
            ],
            "data": data,
        })
