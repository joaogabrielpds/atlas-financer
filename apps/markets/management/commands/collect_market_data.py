
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
            help="Período histórico. Padrão: 1y.",
        )

        parser.add_argument(
            "--ticker",
            type=str,
            help="Coleta somente o ativo informado.",
        )

        parser.add_argument(
            "--full",
            action="store_true",
            help="Força a coleta histórica completa.",
        )

    def handle(self, *args, **options):
        period = options["period"]
        ticker = options["ticker"]
        full = options["full"]

        mode = "histórico completo" if full else "incremental"

        self.stdout.write(
            self.style.NOTICE(
                f"Iniciando coleta {mode}."
            )
        )

        if ticker:
            asset = Asset.objects.filter(
                ticker__iexact=ticker,
                is_active=True,
            ).first()

            if not asset:
                raise CommandError(
                    f"Ativo não encontrado ou inativo: {ticker}"
                )

            try:
                count = collect_asset_history(
                    asset,
                    period=period,
                    full=full,
                )

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
            results = collect_all_assets(
                period=period,
                full=full,
            )

        successful = 0
        failed = 0
        total_records = 0

        for result in results:
            if result["status"] == "success":
                successful += 1
                total_records += result["records"]

                self.stdout.write(
                    self.style.SUCCESS(
                        f"{result['ticker']}: "
                        f"{result['records']} registros processados."
                    )
                )
            else:
                failed += 1

                self.stdout.write(
                    self.style.ERROR(
                        f"{result['ticker']}: {result['message']}"
                    )
                )

        self.stdout.write("")
        self.stdout.write(f"Ativos processados: {len(results)}")
        self.stdout.write(self.style.SUCCESS(f"Sucessos: {successful}"))
        self.stdout.write(self.style.ERROR(f"Falhas: {failed}"))
        self.stdout.write(f"Registros processados: {total_records}")
        self.stdout.write(self.style.SUCCESS("Coleta finalizada."))
