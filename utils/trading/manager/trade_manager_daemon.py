import logging
import traceback
import typing
from datetime import datetime

import numpy as np

import time
from threading import Thread

from apps.core.models import Trade, TriggerOrder
from apps.core.models import Order
from di import MiscProvider
from .exceptions import InvalidTriggerValueException
from .trade_manager import TradeManager
from ..data.models import Candlestick, Instrument

logger = MiscProvider.provide_logger()

class TradeManagerDaemon:

	def __init__(
			self,
			manager: TradeManager,
			sleep_time: float = 1.0,
			same_candle_trigger: bool = True,
			infinite_trigger_liquidity: bool = False
	):
		self.__manager = manager
		self.__repository = self.__manager.get_repository()
		self.__sleep_time = sleep_time
		self.__thread = None
		self.__running = False
		self.__same_candle_trigger = same_candle_trigger
		self.__infinite_trigger_liquidity = infinite_trigger_liquidity
		logger.info(
			f"Initialized {self.__class__.__name__} with manager={manager.__class__.__name__}, "
			f"sleep_time={sleep_time}, same_candle_trigger={same_candle_trigger}, infinite_trigger_liquidity={infinite_trigger_liquidity}"
		)

	def __is_order_active(self, order: TriggerOrder, cs: Candlestick) -> bool:
		time_range = self.__repository.get_candlestick_timerange(cs)
		trigger_time = time_range[1] if self.__same_candle_trigger else time_range[0]
		return trigger_time >= order.open_time

	def __filter_active_orders(self, orders: typing.List[TriggerOrder], candlesticks: typing.Dict[typing.Tuple[str,str], Candlestick]) -> typing.List[TriggerOrder]:
		return list(filter(
			lambda order: self.__is_order_active(order, candlesticks[order.instrument]),
			orders
		))

	def __sort_orders(self, orders: typing.List[TriggerOrder], candlesticks: typing.Dict[Instrument, Candlestick]) -> typing.List[TriggerOrder]:
		def order_priority_score(order: TriggerOrder, candle: Candlestick) -> float:
			CANDLE_TARGET_ALIGNMENT_WEIGHT = 100
			PRICE_WEIGHT = 1
			ORDER_TYPE_WEIGHT = 1e-5


			candle_polarity = np.sign(candle.close - candle.open)
			target_polarity = 1 \
				if (order.is_stop_order and order.units > 0 or order.is_limit_order and order.units < 0) \
				else -1
			order_type = 0 if order.is_trade_related else 1

			candle_target_alignment_score = candle_polarity * target_polarity * CANDLE_TARGET_ALIGNMENT_WEIGHT
			price_score = ((order.price/candle.close) - 1) * target_polarity * PRICE_WEIGHT
			order_type_score = order_type * ORDER_TYPE_WEIGHT

			return candle_target_alignment_score + price_score + order_type_score

		return sorted(
			orders,
			key=lambda order: order_priority_score(order, candlesticks[order.instrument])
		)

	def __get_trigger_price(self, order: TriggerOrder, mid_price: float) -> float:
		return (
			self.__repository.get_ask_price(instrument=order.instrument, price=mid_price)
			if order.units > 0 else
			self.__repository.get_bid_price(instrument=order.instrument, price=mid_price)
		)

	def __fill_order(self, order: Order, enter_price: float):
		try:
			self.__manager.fill_order(
				order,
				price=enter_price
			)
		except InvalidTriggerValueException:
			logger.error(f"Encountered Error upon filling order: {order}.")
			traceback.print_exc()

	def __process_triggered_order(self, order: TriggerOrder, mid_price: float):
		enter_price = mid_price
		if self.__infinite_trigger_liquidity:
			spread_cost = np.sign(order.units) * self.__repository.get_spread_cost(instrument=order.instrument,
																				   price=order.price) / 2
			enter_price = order.price - spread_cost

		self.__fill_order(order, enter_price)

	@staticmethod
	def __get_target_price(order: TriggerOrder, candle: Candlestick) -> float:
		return (
			candle.high
			if (order.is_stop_order and order.units > 0 or order.is_limit_order and order.units < 0) else
			candle.low
		)

	@staticmethod
	def __is_limit_order_triggered(order: Order, trigger_price: float) -> bool:
		return np.sign(order.units) * trigger_price <= np.sign(order.units) * order.price

	@staticmethod
	def __is_stop_order_triggered(order: Order, trigger_price: float) -> bool:
		return np.sign(order.units) * trigger_price >= np.sign(order.units) * order.price

	def __monitor_order(self, order: TriggerOrder, candle: Candlestick):
		mid_price = self.__get_target_price(order, candle)
		trigger_price = self.__get_trigger_price(order, mid_price)

		if (
			(order.is_limit_order and self.__is_limit_order_triggered(order, trigger_price)) or
			(order.is_stop_order and self.__is_stop_order_triggered(order, trigger_price))
		):
			self.__process_triggered_order(order, mid_price)

	def __monitor_trigger_orders(self):
		orders = TriggerOrder.objects.filter(close_time=None)
		candlesticks = {
			instrument: self.__repository.get_latest_candlestick(instrument)
			for instrument in set(map(lambda order: order.instrument, orders))
		}
		orders = self.__filter_active_orders(orders, candlesticks)
		orders = self.__sort_orders(orders, candlesticks)
		for order in orders:
			self.__monitor_order(order, candlesticks[order.instrument])

	def _step(self):
		self.__monitor_trigger_orders()

	def _loop(self):
		while self.__running:
			self._step()
			time.sleep(self.__sleep_time)

	def start(self):
		logger.info(f"Starting trader background manager...")
		self.__thread = Thread(target=self._loop)
		self.__running = True
		self.__thread.start()

	def stop(self):
		logger.info(f"Stopping trader background manager...")
		self.__running = False
		self.__thread.join()
