import typing
import uuid

from django.db import models

from apps.authentication.models import Account
from utils.trading.data.models import Instrument
from datetime import datetime

from .order import Order


class Trade(Order):

	class State:
		open = "OPEN"
		closed = "CLOSED"

	margin_required: float = models.FloatField()
	close_price: typing.Optional[float] = models.FloatField(null=True)
