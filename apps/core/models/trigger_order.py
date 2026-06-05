import typing

from django.db import models

from .order import Order
from .trade import Trade


class TriggerOrder(Order):

	class Type:
		LIMIT = 0
		STOP = 1
		ALL = [LIMIT, STOP]

	trade: typing.Optional[float] = models.ForeignKey(Trade, on_delete=models.CASCADE, default=None, null=True)

	stop_loss: typing.Optional[float] = models.FloatField(null=True)
	take_profit: typing.Optional[float] = models.FloatField(null=True)

	order_type: int = models.IntegerField(choices=[
		(t, t)
		for t in Type.ALL
	])

	@property
	def is_trade_related(self) -> bool:
		return self.trade is not None

	@property
	def is_limit_order(self) -> bool:
		return self.order_type == TriggerOrder.Type.LIMIT

	@property
	def is_stop_order(self) -> bool:
		return self.order_type == TriggerOrder.Type.STOP

	@property
	def is_take_profit(self) -> bool:
		return self.is_trade_related and self.is_limit_order

	@property
	def is_stop_loss(self) -> bool:
		return self.is_trade_related and self.is_stop_order
