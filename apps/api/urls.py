from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views
from apps.markets.views import MarketViewSet, QuoteViewSet
from apps.assets.views import AssetViewSet
from apps.economy.views import EconomicIndicatorViewSet


router = DefaultRouter()

router.register("markets", MarketViewSet, basename="markets")
router.register("assets", AssetViewSet, basename="assets")
router.register("quotes", QuoteViewSet, basename="quotes")
router.register(
    "economy/indicators",
    EconomicIndicatorViewSet,
    basename="indicators"
)


urlpatterns = [
    path("health/", views.health_check, name="health_check"),
    path("", include(router.urls)),
]