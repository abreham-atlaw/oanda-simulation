from django.urls import path

from Oanda.settings import ACCOUNT_ID_KEY
from apps.core.views import CreateOrderView, GetOpenTradesView, GetClosedTradesView, CloseTradeView, GetPricingView, \
    GetCandlestickView, GetInstrumentsView

urlpatterns = [
    path(f'accounts/<uuid:{ACCOUNT_ID_KEY}>/orders/', CreateOrderView.as_view(), name='account-summary'),
    path(f'accounts/<uuid:{ACCOUNT_ID_KEY}>/openTrades/', GetOpenTradesView.as_view(), name='account-summary'),
    path(f'accounts/<uuid:{ACCOUNT_ID_KEY}>/trades/', GetClosedTradesView.as_view(), name='account-summary'),
    path(f'accounts/<uuid:{ACCOUNT_ID_KEY}>/trades/<int:trade_id>/close', CloseTradeView.as_view(), name='account-summary'),
    path(f'accounts/<uuid:{ACCOUNT_ID_KEY}>/pricing/', GetPricingView.as_view(), name='account-summary'),
    path(f'accounts/<uuid:{ACCOUNT_ID_KEY}>/instruments/<str:instrument>/candles/', GetCandlestickView.as_view(), name='account-summary'),
    path(f'accounts/<uuid:{ACCOUNT_ID_KEY}>/instruments/', GetInstrumentsView.as_view(), name='account-summary'),
]
