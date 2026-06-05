import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from django import test

import pandas as pd
import numpy as np

from datetime import datetime, timezone, timedelta

from apps.authentication.models import Account
from apps.core.models import Trade, TriggerOrder
from di.misc_provider import logger
from utils.trading.data.repository.dataframe_repository import DataFrameRepository
from utils.trading.manager import TradeManager
from Oanda import settings


class TradeManagerTest(test.TransactionTestCase):

	def __create_mock_repository(self):
		SIZE = 1000
		df = pd.DataFrame(columns=["v","o","h","l","c","time","base_currency","quote_currency"])
		for col in ["v", "o", "h", "l", "c"]:
			df[col] = (np.sin(np.linspace(0, 3*np.pi, SIZE))*100 + 2000) + 10 * (1 if col == "h" else -1 if col=="l" else 0)
		df["time"] = [(datetime.now() + timedelta(minutes=i - SIZE//2)).replace(tzinfo=timezone.utc).strftime("%Y-%m-%d %H:%M:%S+00:00") for i in range(SIZE)]
		df["base_currency"], df["quote_currency"] = "XAU", "USD"
		return DataFrameRepository(
			df=df,
			time_delta=0,
			spread_cost_percentage_map=settings.SPREAD_COST_PERCENTAGE_MAP,
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
			self.repository,
			weekend_close_market=False
		)

	def test_plot_dataset(self):
		plt.plot(self.repository.df["time"], self.repository.df[["c", "l", "h"]])
		plt.grid()
		plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
		plt.show()

	def test_open_trade(self):
		STOP_LOSS = 1850
		TAKE_PROFIT = 1950
		trade = self.manager.open_trade(
			self.account,
			instrument=("XAU", "USD"),
			units=0.1,
			stop_loss=STOP_LOSS,
			take_profit=TAKE_PROFIT
		)

		open_trades = Trade.objects.filter(account=self.account, close_time=None)
		self.assertEqual(len(open_trades), 1)
		self.assertEqual(trade.id, open_trades.first().id)
		self.assertEqual(len(trade.related_orders), 2)
		self.assertIsNotNone(trade.stop_loss_order)
		self.assertTrue(trade.take_profit_order.is_limit_order)
		self.assertTrue(trade.take_profit_order.is_take_profit)
		self.assertTrue(trade.stop_loss_order.is_stop_order)
		self.assertTrue(trade.stop_loss_order.is_stop_loss)
		self.assertEqual(trade.stop_loss_order.price, STOP_LOSS)
		self.assertEqual(trade.take_profit_order.price, TAKE_PROFIT)

		logger.info(f"Opened a Trade@{trade.price} at {trade.open_time.isoformat()}(Current Time: {self.repository.get_datetime().isoformat()})")

		self.manager.close_trade(trade)

		open_trades = Trade.objects.filter(account=self.account, close_time=None)
		closed_trades = Trade.objects.filter(account=self.account, close_time__isnull=False)
		self.assertEqual(len(open_trades), 0)
		self.assertEqual(len(closed_trades), 1)

	def test_place_limit_order(self):
		order = self.manager.place_order(
			self.account,
			price=2000,
			instrument=("XAU", "USD"),
			units=-0.1,
			order_type=TriggerOrder.Type.LIMIT
		)

		orders = TriggerOrder.objects.filter(account=self.account)
		self.assertEqual(len(orders), 1)
		self.assertEqual(order.id, orders.first().id)
		self.assertTrue(order.is_limit_order)
		self.assertFalse(order.is_stop_order)
		self.assertFalse(order.is_trade_related)

	def test_place_stop_order(self):
		order = self.manager.place_order(
			self.account,
			price=2000,
			instrument=("XAU", "USD"),
			units=0.1,
			order_type=TriggerOrder.Type.STOP
		)

		open_orders = TriggerOrder.objects.filter(account=self.account, close_time=None)
		self.assertEqual(len(open_orders), 1)
		self.assertEqual(order.id, open_orders.first().id)
		self.assertTrue(order.is_stop_order)
		self.assertFalse(order.is_limit_order)
		self.assertFalse(order.is_trade_related)

	def test_cancel_order(self):

		order = self.manager.place_order(
			self.account,
			price=2000,
			instrument=("XAU", "USD"),
			units=0.1,
			order_type=TriggerOrder.Type.STOP
		)
		open_orders = TriggerOrder.objects.filter(account=self.account, close_time=None)
		self.assertEqual(len(open_orders), 1)

		self.manager.cancel_order(order)
		open_orders = TriggerOrder.objects.filter(account=self.account, close_time=None)
		self.assertEqual(len(open_orders), 0)

	def test_fill_order(self):
		ENTER_PRICE = 1950
		STOP_LOSS = 1920
		TAKE_PROFIT = 1980

		order = self.manager.place_order(
			self.account,
			price=ENTER_PRICE,
			instrument=("XAU", "USD"),
			units=0.1,
			order_type=TriggerOrder.Type.STOP,
			stop_loss=STOP_LOSS,
			take_profit=TAKE_PROFIT
		)
		open_trades = Trade.objects.filter(account=self.account, close_time=None)
		open_orders = TriggerOrder.objects.filter(account=self.account, close_time=None)
		self.assertEqual(len(open_orders), 1)
		self.assertEqual(len(open_trades), 0)

		trade = self.manager.fill_order(
			order,
			price=ENTER_PRICE
		)
		open_trades = Trade.objects.filter(account=self.account, close_time=None)
		open_orders = TriggerOrder.objects.filter(account=self.account, close_time=None)
		self.assertEqual(len(open_orders), 2)
		self.assertEqual(len(open_trades), 1)
		self.assertTrue(order not in open_orders)
		self.assertTrue(trade.stop_loss_order.price == STOP_LOSS)
		self.assertTrue(trade.take_profit_order.price == TAKE_PROFIT)
		self.assertTrue(trade.price, ENTER_PRICE)
