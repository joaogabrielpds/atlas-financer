import requests

from datetime import datetime
from decimal import Decimal, InvalidOperation
from datetime import date, datetime
from apps.economy.models import EconomicIndicator


BCB_BASE_URL = "https://api.bcb.gov.br/dados/serie/bcdata.sgs"

INDICATORS = {
    "SELIC_META": {
        "name": "Taxa Selic Meta",
        "code": "432",
        "category": "JUROS",
        "unit": "% a.a.",
        "limit": 20,
    },
    "IPCA": {
        "name": "IPCA mensal",
        "code": "433",
        "category": "INFLACAO",
        "unit": "% a.m.",
        "limit": 12,
    },
}


def collect_bcb_indicator(indicator):
    url = (
        f"{BCB_BASE_URL}.{indicator['code']}"
        f"/dados/ultimos/{indicator['limit']}?formato=json"
    )

    response = requests.get(url, timeout=30)
    response.raise_for_status()

    data = response.json()
    saved = 0

    for item in data:
        reference_date = datetime.strptime(
            item["data"], "%d/%m/%Y"
        ).date()
        if reference_date > date.today():
            continue
        try:
            value = Decimal(item["valor"].replace(",", "."))
        except (InvalidOperation, AttributeError):
            continue

        _, created = EconomicIndicator.objects.update_or_create(
            code=indicator["code"],
            reference_date=reference_date,
            source="BCB-SGS",
            defaults={
                "name": indicator["name"],
                "category": indicator["category"],
                "country": "Brasil",
                "unit": indicator["unit"],
                "value": value,
            },
        )

        if created:
            saved += 1

    return saved


def collect_all_bcb_indicators():
    results = {}

    for key, indicator in INDICATORS.items():
        try:
            saved = collect_bcb_indicator(indicator)
            results[key] = {
                "status": "success",
                "new_records": saved,
            }
        except Exception as error:
            results[key] = {
                "status": "error",
                "message": str(error),
            }

    return results
