import typing
from abc import ABC, abstractmethod

from datetime import datetime

from utils.trading.data.models import Instrument, Candlestick


class CurrencyRepository(ABC):

	@abstractmethod
	def get_instruments(self) -> typing.List[Instrument]:
		pass

	@abstractmethod
	def get_price(self, instrument: Instrument) -> float:
		pass

	@abstractmethod
	def get_spread_cost(self, instrument: Instrument) -> float:
		pass

	@abstractmethod
	def get_candlestick(self, instrument: Instrument, granularity: int, count: int, to: datetime) -> typing.List[Candlestick]:
		pass

	def get_ask_price(self, instrument: Instrument) -> float:
		return self.get_price(instrument) + (self.get_spread_cost(instrument)/2)

	def get_bid_price(self, instrument: Instrument):
		return self.get_price(instrument) - (self.get_spread_cost(instrument)/2)

	def convert(self, units: float, instrument: Instrument) -> float:
		if instrument[0] == instrument[1]:
			return units
		return self.get_price(instrument) * units
