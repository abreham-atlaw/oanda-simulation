from django.urls import path

from Oanda.settings import ACCOUNT_ID_KEY
from apps.core.views import CreateOrderView, GetOpenTradesView, GetClosedTradesView, CloseTradeView, GetPricingView, \
	GetCandlestickView, GetInstrumentsView, GetPendingOrdersView, CancelOrderView

urlpatterns = [
    path(f'accounts/<uuid:{ACCOUNT_ID_KEY}>/orders/', CreateOrderView.as_view() ),
    path(f'accounts/<uuid:{ACCOUNT_ID_KEY}>/pendingOrders/', GetPendingOrdersView.as_view() ),
    path(f'accounts/<uuid:{ACCOUNT_ID_KEY}>/orders/<int:order_id>/cancel', CancelOrderView.as_view() ),
    path(f'accounts/<uuid:{ACCOUNT_ID_KEY}>/openTrades/', GetOpenTradesView.as_view() ),
    path(f'accounts/<uuid:{ACCOUNT_ID_KEY}>/trades/', GetClosedTradesView.as_view() ),
    path(f'accounts/<uuid:{ACCOUNT_ID_KEY}>/trades/<int:trade_id>/close', CloseTradeView.as_view() ),
    path(f'accounts/<uuid:{ACCOUNT_ID_KEY}>/pricing/', GetPricingView.as_view() ),
    path(f'accounts/<uuid:{ACCOUNT_ID_KEY}>/instruments/<str:instrument>/candles/', GetCandlestickView.as_view() ),
    path(f'accounts/<uuid:{ACCOUNT_ID_KEY}>/instruments/', GetInstrumentsView.as_view() ),
]
