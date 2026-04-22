import logging
import typing
from datetime import datetime

import numpy as np

import time
from threading import Thread

from apps.core.models import Trade, LimitOrder
from apps.core.models import Order
from di import MiscProvider
from .trade_manager import TradeManager
from ..data.models import Candlestick

logger = MiscProvider.provide_logger()

class BackgroundTradeManager:

	def __init__(
			self,
			manager: TradeManager,
			sleep_time: float = 1.0
	):
		self.__manager = manager
		self.__repository = self.__manager.get_repository()
		self.__sleep_time = sleep_time
		self.__thread = None
		self.__running = False

	def __get_latest_candlestick(self, order: Order) -> typing.Optional[Candlestick]:
		cs: Candlestick = self.__repository.get_latest_candlestick(order.instrument)
		time_range = self.__repository.get_candlestick_timerange(cs)

		if time_range[1] < order.open_time:
			return None
		return cs

	def __monitor_stop_loss(self):
		for trade in Trade.objects.filter(close_time=None, stop_loss__isnull=False):
			cs = self.__get_latest_candlestick(trade)

			mid_price = cs.low if trade.units > 0 else cs.high
			trigger_price = (
				self.__repository.get_bid_price(instrument=trade.instrument, price=mid_price)
				if trade.units > 0 else
				self.__repository.get_ask_price(instrument=trade.instrument, price=mid_price)
			)

			if np.sign(trade.units) * trigger_price <= np.sign(trade.units) * trade.stop_loss:
				self.__manager.close_trade(trade, price=mid_price)

	def __monitor_take_profit(self):
		for trade in Trade.objects.filter(close_time=None, take_profit__isnull=False):
			cs = self.__get_latest_candlestick(trade)

			if cs is None:
				continue

			mid_price = cs.high if trade.units > 0 else cs.low
			trigger_price = (
				self.__repository.get_bid_price(instrument=trade.instrument, price=mid_price)
				if trade.units > 0 else
				self.__repository.get_ask_price(instrument=trade.instrument, price=mid_price)
			)

			if np.sign(trade.units) * trigger_price >= np.sign(trade.units) * trade.take_profit:
				self.__manager.close_trade(trade, price=mid_price)

	def __monitor_limit_orders(self):
		for order in LimitOrder.objects.filter(close_time=None):
			cs = self.__get_latest_candlestick(order)
			mid_price = cs.low if order.units > 0 else cs.high
			trigger_price = (
				self.__repository.get_ask_price(instrument=order.instrument, price=mid_price)
				if order.units > 0 else
				self.__repository.get_bid_price(instrument=order.instrument, price=mid_price)
			)

			if np.sign(order.units) * trigger_price <= np.sign(order.units) * order.price:
				self.__manager.fill_limit_order(order, price=mid_price)

	def _step(self):
		self.__monitor_stop_loss()
		self.__monitor_take_profit()
		self.__monitor_limit_orders()

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
