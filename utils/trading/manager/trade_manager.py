import typing

from datetime import datetime

import numpy as np

from apps.authentication.models import Account
from apps.core.models import Trade
from di.misc_provider import logger
from utils.devtools import stats
from utils.trading.data.models import Instrument
from utils.trading.data.repository import CurrencyRepository
from .exceptions import InvalidTriggerValueException, MarketClosedException


class TradeManager:

	__WEEKENDS = [5, 6]

	def __init__(
			self,
			repository: CurrencyRepository,
			weekend_close_market: bool = False
	):
		self.__repository = repository
		self.__weekend_close_market = weekend_close_market
		logger.info(
			f"Initialized {self.__class__.__name__} with repository: {repository.__class__.__name__}, "
			f"weekend_close_market: {weekend_close_market}"
		)

	def get_repository(self) -> CurrencyRepository:
		return self.__repository

	def __get_margin_required(self, account: Account, units, instrument, price=None):
		if price is None:
			price = self.__repository.get_price(instrument)
		return account.margin_rate * self.__repository.convert(price * abs(units), (instrument[1], account.currency))

	@stats.track_func(key="TradeManager.get_unrealized_pl")
	def get_unrealized_pl(self, trade: Trade, include_price: bool = False, price: float = None) -> typing.Union[float, typing.Tuple[float, float]]:
		if trade.state == Trade.State.closed:
			return 0

		price = (
			self.__repository.get_ask_price(trade.instrument, price=price)
			if trade.units < 0 else
			self.__repository.get_bid_price(trade.instrument, price=price)
		)

		quote_value = (price - trade.price) * trade.units

		unrealized_pl = self.__repository.convert(quote_value, (trade.instrument[1], trade.account.currency))

		if include_price:
			return unrealized_pl, price
		return unrealized_pl

	def get_account_unrealized_pl(self, account: Account) -> float:
		return sum([
			self.get_unrealized_pl(trade)
			for trade in self.get_open_trades(account)
		])

	@stats.track_func(key="TradeManager.get_nav")
	def get_nav(self, account: Account) -> float:
		return account.balance + self.get_account_unrealized_pl(account)

	@stats.track_func(key="TradeManager.get_margin_used")
	def get_margin_used(self, trade: Trade):
		return self.__get_margin_required(
			account=trade.account,
			instrument=trade.instrument,
			units=trade.units,
		)

	def get_account_margin_used(self, account: Account) -> float:
		return sum([
			self.get_margin_used(trade)
			for trade in self.get_open_trades(account)
		])

	@stats.track_func(key="TradeManager.get_margin_available")
	def get_margin_available(self, account: Account) -> float:
		return self.get_nav(account) - self.get_account_margin_used(account)

	@stats.track_func(key="TradeManager.get_open_trades")
	def get_open_trades(self, account: Account) -> typing.List[Trade]:
		return Trade.objects.filter(account=account, close_time=None)

	@staticmethod
	def __validate_triggers(units: int, price: float, take_profit: float = None, stop_loss: float = None) -> bool:

		def validate_value(action: int, price: float, trigger: float, trigger_direction: int) -> bool:
			if trigger is None:
				return True
			return action * trigger_direction * (trigger - price) > 0

		action = np.sign(units)

		return validate_value(action, price, take_profit, 1) and validate_value(action, price, stop_loss, -1)

	def __validate_trade(
		self,
		units: int,
		price: float,
		stop_loss: float | None = None,
		take_profit: float | None = None
	):

		now = self.__repository.get_datetime()

		if self.__weekend_close_market and now.weekday() in self.__WEEKENDS:
			raise MarketClosedException(now)

		if not self.__validate_triggers(units, price, take_profit, stop_loss):
			raise InvalidTriggerValueException(take_profit, stop_loss, price, units)

	def open_trade(
			self,
			account: Account,
			instrument: Instrument,
			units: int,
			stop_loss: float | None = None,
			take_profit: float | None = None
	) -> Trade:

		if units < 0:
			price = self.__repository.get_bid_price(instrument)
		else:
			price = self.__repository.get_ask_price(instrument)

		margin_required = self.__get_margin_required(
			account=account,
			units=units,
			instrument=instrument,
			price=price
		)

		self.__validate_trade(
			units, price, stop_loss, take_profit
		)

		return Trade.objects.create(
			account=account,
			price=price,
			units=units,
			margin_required=margin_required,
			base_currency=instrument[0],
			quote_currency=instrument[1],
			open_time=self.__repository.get_datetime(),
			stop_loss=stop_loss,
			take_profit=take_profit
		)

	def close_trade(self, trade: Trade, close_time: datetime = None, price: float = None):

		if close_time is None:
			close_time = self.__repository.get_datetime()

		pl, price = self.get_unrealized_pl(trade, include_price=True, price=price)
		trade.realized_pl = pl

		trade.close_time = close_time
		trade.close_price = price
		trade.save()

		trade.account.balance += pl
		trade.account.save()
