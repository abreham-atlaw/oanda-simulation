from django.urls import path

from Oanda.settings import ACCOUNT_ID_KEY
from .views import AccountSummaryView

urlpatterns = [
    path(f'accounts/<uuid:{ACCOUNT_ID_KEY}>/summary/', AccountSummaryView.as_view(), name='account-summary'),
]
