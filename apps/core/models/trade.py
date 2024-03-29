import typing
import uuid

from django.db import models

from apps.authentication.models import Account
from utils.trading.data.models import Instrument
from datetime import datetime


class Trade(models.Model):

	class State:
		open = "OPEN"
		closed = "CLOSED"

	id: int = models.AutoField(primary_key=True)
	account: Account = models.ForeignKey(Account, on_delete=models.CASCADE)
	price: float = models.FloatField()
	realized_pl: typing.Optional[float] = models.FloatField(default=0.0)
	units: float = models.IntegerField()
	margin_required: float = models.FloatField()
	base_currency: str = models.CharField(max_length=3)
	quote_currency: str = models.CharField(max_length=3)
	open_time: datetime = models.DateTimeField(auto_now_add=True)
	close_time: typing.Optional[datetime] = models.DateTimeField(null=True)

	@property
	def state(self) -> str:
		if self.close_time is None:
			return Trade.State.open
		return Trade.State.closed

	@property
	def instrument(self) -> Instrument:
		return self.base_currency, self.quote_currency
