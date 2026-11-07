
from django.urls import path

from .views import TechnicalIndicatorsView

app_name = "technical"

urlpatterns = [
    path(
        "<str:ticker>/",
        TechnicalIndicatorsView.as_view(),
        name="indicators",
    ),
]
