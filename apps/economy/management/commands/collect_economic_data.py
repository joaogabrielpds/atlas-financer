
from django.core.management.base import BaseCommand, CommandError

from apps.assets.models import Asset
from apps.markets.services.yahoo_finance import (
    collect_all_assets,
    collect_asset_history,
)


class Command(BaseCommand):
    help = "Coleta e atualiza o histórico de cotações dos ativos."

    def add_arguments(self, parser):
        parser.add_argument(
            "--period",
            type=str,
            default="1y",
            choices=[
                "1mo", "3mo", "6mo", "1y",
                "2y", "5y", "10y", "max",
            ],
            help="Período histórico para coleta. Padrão: 1y.",
        )

        parser.add_argument(
            "--ticker",
            type=str,
            help="Coleta somente o ativo informado.",
        )

    def handle(self, *args, **options):
        period = options["period"]
        ticker = options["ticker"]

        self.stdout.write(
            self.style.NOTICE(
                f"Iniciando coleta de cotações: período {period}"
            )
        )

        if ticker:
            asset = Asset.objects.filter(
                ticker__iexact=ticker,
                is_active=True,
            ).first()

            if not asset:
                raise CommandError(
                    f"Ativo ativo não encontrado: {ticker}"
                )

            try:
                count = collect_asset_history(asset, period)

                results = [{
                    "ticker": asset.ticker,
                    "status": "success",
                    "records": count,
                }]

            except Exception as error:
                results = [{
                    "ticker": asset.ticker,
                    "status": "error",
                    "message": str(error),
                }]
        else:
            results = collect_all_assets(period)

        successful = 0
        failed = 0
        total_records = 0

        for result in results:
            ticker_name = result["ticker"]

            if result["status"] == "success":
                records = result["records"]
                successful += 1
                total_records += records

                self.stdout.write(
                    self.style.SUCCESS(
                        f"{ticker_name}: {records} registros processados."
                    )
                )
            else:
                failed += 1

                self.stdout.write(
                    self.style.ERROR(
                        f"{ticker_name}: {result['message']}"
                    )
                )

        self.stdout.write("")
        self.stdout.write("Resumo da coleta:")
        self.stdout.write(f"Ativos processados: {len(results)}")
        self.stdout.write(
            self.style.SUCCESS(f"Sucessos: {successful}")
        )
        self.stdout.write(
            self.style.ERROR(f"Falhas: {failed}")
        )
        self.stdout.write(f"Registros processados: {total_records}")
        self.stdout.write(
            self.style.SUCCESS("Coleta finalizada.")
        )
