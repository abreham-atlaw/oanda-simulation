import time
import unittest
from datetime import datetime, timezone, timedelta

import numpy as np
import pandas as pd
from django import test

from Oanda import settings
from apps.authentication.models import Account
from apps.core.models import Trade
from di import MiscProvider
from utils.trading.data.repository.dataframe_repository import DataFrameRepository
from utils.trading.manager import BackgroundTradeManager, TradeManager

logger = MiscProvider.provide_logger()

class BackgroundTradeManagerTest(test.TransactionTestCase):

	def __create_mock_repository(self):
		SIZE = 1000
		df = pd.DataFrame(columns=["v","o","h","l","c","time","base_currency","quote_currency"])
		for col in ["v", "o", "h", "l", "c"]:
			df[col] = np.arange(SIZE) + 1
		# TIME FORMAT: 2023-09-22 08:31:00+00:00
		df["time"] = [(datetime.now() + timedelta(minutes=i - SIZE//2)).replace(tzinfo=timezone.utc).strftime("%Y-%m-%d %H:%M:%S+00:00") for i in range(SIZE)]
		df["base_currency"], df["quote_currency"] = "AUD", "USD"
		return DataFrameRepository(
			df=df,
			time_delta=0,
			spread_cost_percentage=settings.SPREAD_COST_PERCENTAGE,
			delta_multiplier=60
		)

	def setUp(self):
		super().setUp()
		self.account = Account.objects.create(
			balance=100.0,
			alias="Test Account 0",
			margin_rate=0,
			delta_multiplier=1,
			time_delta=0
		)
		self.repository = self.__create_mock_repository()
		self.manager = TradeManager(
			self.repository
		)
		self.bg_manager = BackgroundTradeManager(
			manager=self.manager
		)
		self.bg_manager.start()

	def tearDown(self):
		self.bg_manager.stop()

	def test_background_trade_manager(self):
		instrument = ("AUD", "USD")

		INCREMENT = 10

		price = self.repository.get_price(instrument)
		stop_loss = price + INCREMENT
		logger.info(f"Entering Trade @ {price} with Stop Loss @ {stop_loss}")
		trade = self.manager.open_trade(
			account=self.account,
			instrument=("AUD", "USD"),
			units=-100,
			stop_loss=stop_loss
		)

		self.assertIsNotNone(trade.stop_loss)

		time.sleep(INCREMENT//2)
		logger.info(f"Slept {INCREMENT // 2}. Price: {self.repository.get_price(instrument)}")
		trade = Trade.objects.get(id=trade.id)
		self.assertEqual(trade.close_time, None)

		time.sleep(INCREMENT)
		logger.info(f"Slept {INCREMENT}. Price: {self.repository.get_price(instrument)}")
		trade = Trade.objects.get(id=trade.id)
		self.assertIsNotNone(trade.close_time)

		print(f"Trade Closed at: {trade.close_time}@{trade.close_price}")
