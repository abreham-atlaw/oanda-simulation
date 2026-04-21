import typing

from django.db import models

from datetime import datetime

from apps.authentication.models import Account
from utils.trading.data.models import Instrument


class Order(models.Model):

	class State:
		open = "OPEN"
		closed = "CLOSED"

	id: int = models.AutoField(primary_key=True)
	account: Account = models.ForeignKey(Account, on_delete=models.CASCADE)
	price: float = models.FloatField()
	realized_pl: typing.Optional[float] = models.FloatField(default=0.0)
	units: float = models.FloatField()
	base_currency: str = models.CharField(max_length=3)
	quote_currency: str = models.CharField(max_length=3)
	open_time: datetime = models.DateTimeField()
	close_time: typing.Optional[datetime] = models.DateTimeField(null=True)

	stop_loss: typing.Optional[float] = models.FloatField(null=True)
	take_profit: typing.Optional[float] = models.FloatField(null=True)

	@property
	def state(self) -> str:
		if self.close_time is None:
			return Order.State.open
		return Order.State.closed

	class Meta:
		abstract=True

	@property
	def is_closed(self) -> bool:
		return self.close_time is not None

	@property
	def instrument(self) -> Instrument:
		return self.base_currency, self.quote_currency
