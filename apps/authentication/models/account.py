import uuid
from datetime import datetime

from django.db import models


class Account(models.Model):

	id = models.UUIDField(primary_key=True, default=uuid.uuid4)
	balance: float = models.FloatField()
	alias: str = models.CharField(max_length=255)
	currency: str = models.CharField(default="USD", max_length=255)
	margin_rate: float = models.FloatField()
	time_delta: int = models.IntegerField(default=0)

	def __str__(self):
		return self.alias
