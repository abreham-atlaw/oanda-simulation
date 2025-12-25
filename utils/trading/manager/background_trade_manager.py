import logging

import numpy as np

import time
from threading import Thread

from apps.core.models import Trade
from di import MiscProvider
from .trade_manager import TradeManager


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

	def __monitor_stop_loss(self):
		for trade in Trade.objects.filter(close_time=None, stop_loss__isnull=False):
			if np.sign(trade.units) * self.__repository.get_price(trade.instrument) <= np.sign(trade.units) * trade.stop_loss:
				self.__manager.close_trade(trade)

	def __monitor_take_profit(self):
		for trade in Trade.objects.filter(close_time=None, take_profit__isnull=False):
			if np.sign(trade.units) * self.__repository.get_price(trade.instrument) >= np.sign(trade.units) * trade.take_profit:
				self.__manager.close_trade(trade)

	def _step(self):
		self.__monitor_stop_loss()
		self.__monitor_take_profit()

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
