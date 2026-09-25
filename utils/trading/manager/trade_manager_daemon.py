import typing

import time
import traceback
from datetime import datetime
from threading import Thread

import numpy as np

from di import MiscProvider
from apps.core.models import Order
from apps.core.models import TriggerOrder
from utils.trading.data.models import Candlestick, Instrument
from .trade_manager import TradeManager
from .exceptions import InvalidTriggerValueException

logger = MiscProvider.provide_logger()

class TradeManagerDaemon:

	def __init__(
			self,
			manager: TradeManager,
			sleep_time: float = 1.0,
			same_candle_trigger: bool = True,
			infinite_trigger_liquidity: bool = False,
			price_point_smoothing_n: int = 2,
	):
		self.__manager = manager
		self.__repository = self.__manager.get_repository()
		self.__sleep_time = sleep_time
		self.__thread = None
		self.__running = False
		self.__same_candle_trigger = same_candle_trigger
		self.__infinite_trigger_liquidity = infinite_trigger_liquidity
		self.__price_point_smoothing_n = price_point_smoothing_n
		self.__processed_candlesticks_store: typing.Dict[Instrument, Candlestick] = None
		logger.info(
			f"Initialized {self.__class__.__name__} with manager={manager.__class__.__name__}, "
			f"sleep_time={sleep_time}, same_candle_trigger={same_candle_trigger}, infinite_trigger_liquidity={infinite_trigger_liquidity}, "
			f"price_point_smoothing_n={price_point_smoothing_n}"
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

	@staticmethod
	def __sort_orders(
			orders: typing.List[TriggerOrder],
			prices: typing.Dict[Instrument, float],
			previous_prices: typing.Dict[Instrument, typing.Optional[float]]
	) -> typing.List[TriggerOrder]:
		def order_priority_score(order: TriggerOrder, price: float, previous_price: typing.Optional[float]) -> float:
			CANDLE_TARGET_ALIGNMENT_WEIGHT = 100
			PRICE_WEIGHT = 1
			ORDER_TYPE_WEIGHT = 1e-5


			candle_polarity = np.sign(price - previous_price) if previous_price is not None else 1.0  # TODO: Use previous candlestick for finding open value polarity
			target_polarity = 1 \
				if (order.is_stop_order and order.units > 0 or order.is_limit_order and order.units < 0) \
				else -1
			order_type = 0 if order.is_trade_related else 1

			candle_target_alignment_score = candle_polarity * target_polarity * CANDLE_TARGET_ALIGNMENT_WEIGHT
			price_score = ((order.price/price) - 1) * target_polarity * PRICE_WEIGHT
			order_type_score = order_type * ORDER_TYPE_WEIGHT

			return candle_target_alignment_score + price_score + order_type_score

		return sorted(
			orders,
			key=lambda order: order_priority_score(
				order,
				price=prices[order.instrument],
				previous_price=previous_prices[order.instrument]
			)
		)

	def __get_trigger_price(self, order: TriggerOrder, mid_price: float) -> float:
		return (
			self.__repository.get_ask_price(instrument=order.instrument, price=mid_price)
			if order.units > 0 else
			self.__repository.get_bid_price(instrument=order.instrument, price=mid_price)
		)

	def __fill_order(self, order: Order, enter_price: float, open_time: datetime):
		try:
			self.__manager.fill_order(
				order,
				price=enter_price,
				open_time=open_time
			)
		except InvalidTriggerValueException:
			logger.error(f"Encountered Error upon filling order: {order}.")
			traceback.print_exc()

	def __process_triggered_order(self, order: TriggerOrder, mid_price: float, open_time: datetime):
		enter_price = mid_price
		if self.__infinite_trigger_liquidity:
			spread_cost = np.sign(order.units) * self.__repository.get_spread_cost(instrument=order.instrument,
																				   price=order.price) / 2
			enter_price = order.price - spread_cost

		self.__fill_order(order, enter_price, open_time=open_time)

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

	def __monitor_order(self, order: TriggerOrder, price: float, candlestick: Candlestick):
		mid_price = price
		trigger_price = self.__get_trigger_price(order, mid_price)

		if (
			(order.is_limit_order and self.__is_limit_order_triggered(order, trigger_price)) or
			(order.is_stop_order and self.__is_stop_order_triggered(order, trigger_price))
		):
			cs_time_range = self.__repository.get_candlestick_timerange(candlestick)
			open_time = cs_time_range[0] + (cs_time_range[1] - cs_time_range[0])/2
			self.__process_triggered_order(order, mid_price, open_time=open_time)

	def __generate_price_points(self, candlestick: Candlestick) -> typing.List[float]:
		if candlestick.close >= candlestick.open:
			price_points = [
				candlestick.open, candlestick.low, candlestick.high, candlestick.close
			]
		else:
			price_points = [
				candlestick.open, candlestick.high, candlestick.low, candlestick.close
			]

		if self.__price_point_smoothing_n > 0:
			price_points = np.append(
				np.concatenate([
					np.linspace(price_points[i], price_points[i+1], 2 + self.__price_point_smoothing_n)[:-1]
					for i in range(len(price_points) - 1)
				]),
				price_points[-1]
			)

		return price_points

	def __simulate_price_point(
			self,
			price_points: typing.Dict[Instrument, float],
			previous_price_points: typing.Dict[Instrument, typing.Optional[float]],
			candlesticks: typing.Dict[Instrument, Candlestick]
	):
		orders = TriggerOrder.objects.filter(close_time=None)
		orders = self.__filter_active_orders(orders, candlesticks)
		orders = self.__sort_orders(orders, price_points, previous_price_points)

		for order in orders:
			self.__monitor_order(order, price=price_points[order.instrument], candlestick=candlesticks[order.instrument])

	def __is_candlesticks_processed(self, candlesticks: typing.Dict[Instrument, Candlestick]) -> bool:

		if self.__processed_candlesticks_store is None:
			return False

		return any([
			candlesticks.get(instrument).time <= self.__processed_candlesticks_store.get(instrument).time
			for instrument in candlesticks.keys()
		])

	def __monitor_trigger_orders(self):
		candlesticks = {
			instrument: self.__repository.get_latest_candlestick(instrument)
			for instrument in self.__repository.get_instruments()
		}

		if self.__is_candlesticks_processed(candlesticks):
			return

		price_points = {
			instrument: self.__generate_price_points(cs)
			for instrument, cs in candlesticks.items()
		}

		assert (len(set([len(pps) for pps in price_points.values()])) == 1)

		price_points_size = len(next(iter(price_points.values())))

		for i in range(price_points_size):
			current_prices = {
				instrument: instrument_prices[i]
				for instrument, instrument_prices in price_points.items()
			}
			previous_prices = {
				instrument: instrument_prices[i - 1]
				if i > 0 else None
				for instrument, instrument_prices in price_points.items()
			}

			self.__simulate_price_point(
				price_points=current_prices,
				previous_price_points=previous_prices,
				candlesticks=candlesticks
			)

		self.__processed_candlesticks_store = candlesticks.copy()

	def _step(self):
		self.__monitor_trigger_orders()

	def _loop(self):
		while self.__running:
			self._step()
			time.sleep(self.__sleep_time)

	def start(self):
		logger.info(f"Starting trader background manager...")
		self.__thread = Thread(target=self._loop, daemon=True)
		self.__running = True
		self.__thread.start()

	def stop(self):
		logger.info(f"Stopping trader background manager...")
		self.__running = False
		self.__thread.join()
