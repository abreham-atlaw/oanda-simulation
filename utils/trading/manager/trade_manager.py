import typing

from datetime import datetime

from apps.authentication.models import Account
from apps.core.models import Trade
from utils.devtools import stats
from utils.trading.data.models import Instrument
from utils.trading.data.repository import CurrencyRepository


class TradeManager:

	def __init__(self, repository: CurrencyRepository):
		self.__repository = repository

	def __get_margin_required(self, account: Account, units, instrument, price=None):
		if price is None:
			price = self.__repository.get_price(instrument)
		return account.margin_rate * self.__repository.convert(price * abs(units), (instrument[1], account.currency))

	@stats.track_func(key="TradeManager.get_unrealized_pl")
	def get_unrealized_pl(self, trade: Trade, include_price: bool = False) -> typing.Union[float, typing.Tuple[float, float]]:
		if trade.state == Trade.State.closed:
			return 0
		price = self.__repository.get_price(trade.instrument)
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

	def open_trade(self, account: Account, instrument: Instrument, units: int) -> Trade:

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

		return Trade.objects.create(
			account=account,
			price=price,
			units=units,
			margin_required=margin_required,
			base_currency=instrument[0],
			quote_currency=instrument[1],
			open_time=self.__repository.get_datetime()
		)

	def close_trade(self, trade: Trade):
		pl, price = self.get_unrealized_pl(trade, include_price=True)
		trade.realized_pl = pl
		trade.close_time = self.__repository.get_datetime()
		trade.close_price = price
		trade.save()

		trade.account.balance += pl
		trade.account.save()
