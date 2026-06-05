import typing

from django.db import models

from .order import Order


class Trade(Order):

	class State:
		open = "OPEN"
		closed = "CLOSED"

	margin_required: float = models.FloatField()
	close_price: typing.Optional[float] = models.FloatField(null=True)

	@property
	def related_orders(self) -> typing.List[Order]:
		from .trigger_order import TriggerOrder
		return TriggerOrder.objects.filter(trade=self)

	@property
	def stop_loss_order(self) -> typing.Union[typing.Union[Order, 'TriggerOrder']]:
		from .trigger_order import TriggerOrder

		orders: typing.List[TriggerOrder] = self.related_orders
		for order in orders:
			if order.is_stop_order:
				return order
		return None

	@property
	def take_profit_order(self) -> typing.Union[typing.Union[Order, 'TriggerOrder']]:
		from .trigger_order import TriggerOrder

		orders: typing.List[TriggerOrder] = self.related_orders
		for order in orders:
			if order.is_take_profit:
				return order
		return None

	@property
	def stop_loss(self) -> typing.Optional[float]:
		return self.stop_loss_order.price if self.stop_loss_order is not None else None

	@property
	def take_profit(self) -> typing.Optional[float]:
		return self.take_profit_order.price if self.take_profit_order is not None else None