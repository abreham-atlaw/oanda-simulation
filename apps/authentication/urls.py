from django.urls import path

from Oanda.settings import ACCOUNT_ID_KEY
from .views import AccountSummaryView, CreateAccountView

urlpatterns = [
    path(f'accounts/<uuid:{ACCOUNT_ID_KEY}>/summary/', AccountSummaryView.as_view(), name='account-summary'),
    path(f"accounts/create/", CreateAccountView.as_view(), name="create-account"),
]
