import time
import typing
import unittest
from datetime import datetime, timezone, timedelta

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from django import test

from Oanda import settings
from apps.authentication.models import Account
from apps.core.models import Trade, TriggerOrder
from di import MiscProvider
from utils.trading.data.repository.dataframe_repository import DataFrameRepository
from utils.trading.manager import TradeManagerDaemon, TradeManager

logger = MiscProvider.provide_logger()

class TradeManagerDaemonTest(test.TransactionTestCase):

	@staticmethod
	def __generate_sinusoidal_values(df: pd.DataFrame, size: int):
		for col in ["v", "o", "h", "l", "c"]:
			df[col] = (np.sin(np.linspace(0, 4 * np.pi, size)) * 100 + 2000) + 10 * (
				1 if col == "h" else -1 if col == "l" else 0)

	def __create_expception_value_generator(
			self,
			constant_values: typing.Tuple[float, float, float, float],
			exception_values: typing.Tuple[float, float, float, float],
			placement: float
	) -> typing.Callable[[pd.DataFrame, int], None]:

			assert len(constant_values) == len(exception_values) == 4
			assert 0 <= placement <= 1.0

			def generate_exception_values(df: pd.DataFrame, size: int):
				placement_idx = int(size * placement)

				values = [
					np.zeros(size) + constant_values[i]
					for i in range(len(constant_values))
				]
				for i in range(4):
					values[i][placement_idx] = exception_values[i]

				df["c"], df["l"], df["h"], df["o"] = values

				df["v"] = np.zeros(size) + 100

			return generate_exception_values

	def __create_mock_repository(
			self,
			generator: typing.Callable[[pd.DataFrame, int], None],
			size: int,
			delta_multiplier: float
	):
		SIZE = size
		df = pd.DataFrame(columns=["v", "o", "h", "l", "c", "time", "base_currency", "quote_currency"])

		df["time"] = [(datetime.now() + timedelta(minutes=i - SIZE // 2)).replace(tzinfo=timezone.utc).strftime(
			"%Y-%m-%d %H:%M:%S+00:00") for i in range(SIZE)]
		generator(df, SIZE)
		df["base_currency"], df["quote_currency"] = self.instrument
		return DataFrameRepository(
			df=df,
			time_delta=0,
			spread_cost_percentage_map=settings.SPREAD_COST_PERCENTAGE_MAP,
			delta_multiplier=delta_multiplier
		)

	@staticmethod
	def __clean_orders():
		TriggerOrder.objects.all().delete()
		Trade.objects.all().delete()

	def _setUp(
			self,
			generator=None,
			size=500,
			delta_multiplier: float = 120
	):
		if generator is None:
			generator = self.__generate_sinusoidal_values
		self.instrument = ("XAU", "USD")
		self.account = Account.objects.create(
			balance=100.0,
			alias="Test Account 0",
			margin_rate=0,
			delta_multiplier=1,
			time_delta=0
		)
		self.repository = self.__create_mock_repository(generator=generator, size=size, delta_multiplier=delta_multiplier)
		self.manager = TradeManager(
			self.repository
		)
		self.manager_daemon = TradeManagerDaemon(
			manager=self.manager,
			infinite_trigger_liquidity=True
		)
		self.manager_daemon.start()
		self.__clean_orders()

	def tearDown(self):
		self.manager_daemon.stop()
		self.__clean_orders()
		plt.close()

	def test_plot_dataset(self):
		self._setUp()
		plt.plot(self.repository.df["time"], self.repository.df[["c", "l", "h"]])
		plt.grid()
		plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
		plt.show()

	def __plot_price(self, ax: plt.Axes, current_price: float, current_time: datetime, target_price: float, end_price: float):
		ax.cla()
		ax.grid()
		ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))

		ax.plot(self.repository.df["time"], self.repository.df[["c", "l", "h", "o"]], label=["c", "l", "h", "o"])
		plt.legend()
		ax.axhline(y=target_price, color="purple")
		ax.axhline(y=end_price, color="red")
		ax.scatter([current_time], [current_price], color="red")
		plt.pause(0.1)

	def __test_order(
			self,
			order_function: typing.Callable,
			expected_trades: int,
			expected_orders: int,
			plot_function: typing.Callable,
			success_check: typing.Callable,
			assert_function: typing.Callable = None
	):
		order_function()

		fig, ax = plt.subplots()

		while True:
			current_time = self.repository.get_datetime()
			current_price = self.repository.get_price(instrument=self.instrument)

			open_trades = Trade.objects.filter(account=self.account, close_time=None)
			open_orders = TriggerOrder.objects.filter(account=self.account, close_time=None)
			logger.info(
				f"Time: {current_time.isoformat()}, Price: {current_price :.5f}, Open Trades: {len(open_trades)}, Active Orders: {len(open_orders)}"
			)

			plot_function(ax, current_price, current_time)

			if success_check(current_price):
				self.assertEqual(len(open_trades), expected_trades)
				self.assertEqual(len(open_orders), expected_orders)
				if assert_function is not None:
					assert_function()
				break

			time.sleep(1)

	def __test_order_fill(
			self,
			order_price_return: float,
			units: float,
			order_type: int,
			end_price_callback: typing.Callable,
			success_check: typing.Callable,
	):

		def order_function():
			self.manager.place_order(
				account=self.account,
				instrument=self.instrument,
				units=units,
				price=ORDER_PRICE,
				order_type=order_type
			)
			logger.info(
				f"Placed {units} units {'LIMIT' if order_type == TriggerOrder.Type.LIMIT else 'STOP'} Order@{ORDER_PRICE}"
			)

		start_price  = self.repository.get_price(self.instrument)
		ORDER_PRICE = order_price_return * start_price
		END_PRICE = end_price_callback(ORDER_PRICE)

		self.__test_order(
			order_function=order_function,
			expected_orders=0,
			expected_trades=1,
			plot_function=lambda ax, current_price, current_time: self.__plot_price(ax, current_price, current_time, ORDER_PRICE, END_PRICE),
			success_check=lambda current_price: success_check(current_price, END_PRICE)
		)

	def test_buy_stop_order_fill(self):
		self._setUp()
		self.__test_order_fill(
			1.025,
			units=0.1,
			order_type=TriggerOrder.Type.STOP,
			end_price_callback=lambda price: price,
			success_check=lambda current_price, end_price: current_price > end_price
		)

	def test_sell_stop_order_fill(self):
		self._setUp()
		self.__test_order_fill(
			0.995,
			units=-0.1,
			order_type=TriggerOrder.Type.STOP,
			end_price_callback=lambda price: price,
			success_check=lambda current_price, end_price: current_price < end_price
		)

	def test_buy_limit_order_fill(self):
		self._setUp()
		self.__test_order_fill(
			0.995,
			units=0.1,
			order_type=TriggerOrder.Type.LIMIT,
			end_price_callback=lambda price: price,
			success_check=lambda current_price, end_price: current_price < end_price
		)

	def test_sell_limit_order_fill(self):
		self._setUp()
		self.__test_order_fill(
			1.05,
			units=-0.1,
			order_type=TriggerOrder.Type.LIMIT,
			end_price_callback=lambda price: price,
			success_check=lambda current_price, end_price: current_price > end_price
		)

	def __test_trade_with_triggers(
			self,
			take_profit_return: float,
			stop_loss_return: float,
			units: float,
			end_price_callback: typing.Callable,
			success_check: typing.Callable
	):

		def order_function():
			trade = self.manager.open_trade(
				account=self.account,
				instrument=self.instrument,
				units=units,
				take_profit=TAKE_PROFIT,
				stop_loss=STOP_LOSS,
			)
			logger.info(f"Opened a trade@{trade.price} with take_profit={TAKE_PROFIT} & stop_loss={STOP_LOSS}")

		start_price = self.repository.get_price(self.instrument)
		TAKE_PROFIT = start_price * take_profit_return if take_profit_return is not None else None
		STOP_LOSS = start_price * stop_loss_return if stop_loss_return is not None else None
		END_PRICE = end_price_callback(TAKE_PROFIT, STOP_LOSS)

		self.__test_order(
			order_function=order_function,
			expected_orders=0,
			expected_trades=0,
			plot_function=lambda ax, current_price, current_time: self.__plot_price(ax, current_price, current_time, TAKE_PROFIT or STOP_LOSS, END_PRICE),
			success_check=lambda current_price: success_check(current_price, END_PRICE)
		)

	def test_buy_trade_with_take_profit(self):
		self._setUp()
		self.__test_trade_with_triggers(
			take_profit_return=1.025,
			stop_loss_return=None,
			units=0.1,
			end_price_callback=lambda take_profit, stop_loss: take_profit,
			success_check=lambda current_price, end_price: current_price > end_price
		)

	def test_buy_trade_with_stop_loss(self):
		self._setUp()
		self.__test_trade_with_triggers(
			take_profit_return=None,
			stop_loss_return=0.975,
			units=0.1,
			end_price_callback=lambda take_profit, stop_loss: stop_loss,
			success_check=lambda current_price, end_price: current_price < end_price
		)

	def test_sell_trade_with_take_profit(self):
		self._setUp()
		self.__test_trade_with_triggers(
			take_profit_return=0.975,
			stop_loss_return=None,
			units=-0.1,
			end_price_callback=lambda take_profit, stop_loss: take_profit,
			success_check=lambda current_price, end_price: current_price < end_price
		)

	def test_sell_trade_with_stop_loss(self):
		self._setUp()
		self.__test_trade_with_triggers(
			take_profit_return=None,
			stop_loss_return=1.025,
			units=-0.1,
			end_price_callback=lambda take_profit, stop_loss: stop_loss,
			success_check=lambda current_price, end_price: current_price > end_price
		)

	def __test_trade_trigger_priority(
			self,
			take_profit_return: float,
			stop_loss_return: float,
			order_return: float,
			order_type: int,
			trade_units: float,
			order_units: float,
			end_price_callback: typing.Callable,
			success_check: typing.Callable
	):

		def order_function():
			trade = self.manager.open_trade(
				account=self.account,
				instrument=self.instrument,
				units=trade_units,
				take_profit=TAKE_PROFIT,
				stop_loss=STOP_LOSS,
			)
			logger.info(f"Opened a trade@{trade.price} with take_profit={TAKE_PROFIT} & stop_loss={STOP_LOSS}")
			order = self.manager.place_order(
				account=self.account,
				instrument=self.instrument,
				units=order_units,
				price=ORDER_PRICE,
				order_type=order_type
			)
			logger.info(
				f"Placed {order_units} units {'LIMIT' if order_type == TriggerOrder.Type.LIMIT else 'STOP'} Order@{ORDER_PRICE}"
			)


		start_price = self.repository.get_price(self.instrument)
		TAKE_PROFIT = start_price * take_profit_return if take_profit_return is not None else None
		STOP_LOSS = start_price * stop_loss_return if stop_loss_return is not None else None
		ORDER_PRICE = start_price * order_return
		END_PRICE = end_price_callback(ORDER_PRICE)

		self.__test_order(
			order_function=order_function,
			expected_orders=0,
			expected_trades=1,
			plot_function=lambda ax, current_price, current_time: self.__plot_price(ax, current_price, current_time,
																					ORDER_PRICE, END_PRICE),
			success_check=lambda current_price: success_check(current_price, END_PRICE)
		)

	def test_buy_stop_loss_priority_over_sell_stop_order(self):
		self._setUp()
		self.__test_trade_trigger_priority(
			take_profit_return=None,
			stop_loss_return=0.975,
			order_return=0.975,
			order_type=TriggerOrder.Type.STOP,
			trade_units=0.1,
			order_units=-0.1,
			end_price_callback=lambda order_price: order_price,
			success_check=lambda current_price, end_price: current_price < end_price
		)

	def test_buy_take_profit_priority_over_sell_limit_order(self):
		self._setUp()
		self.__test_trade_trigger_priority(
			take_profit_return=1.025,
			stop_loss_return=None,
			order_return=1.025,
			order_type=TriggerOrder.Type.LIMIT,
			trade_units=0.1,
			order_units=-0.1,
			end_price_callback=lambda order_price: order_price,
			success_check=lambda current_price, end_price: current_price > end_price
		)

	def test_sell_stop_loss_priority_over_buy_stop_order(self):
		self._setUp()
		self.__test_trade_trigger_priority(
			take_profit_return=None,
			stop_loss_return=1.025,
			order_return=1.025,
			order_type=TriggerOrder.Type.STOP,
			trade_units=-0.1,
			order_units=0.1,
			end_price_callback=lambda order_price: order_price,
			success_check=lambda current_price, end_price: current_price > end_price
		)

	def test_sell_take_profit_priority_over_buy_limit_order(self):
		self._setUp()
		self.__test_trade_trigger_priority(
			take_profit_return=0.975,
			stop_loss_return=None,
			order_return=0.975,
			order_type=TriggerOrder.Type.LIMIT,
			trade_units=-0.1,
			order_units=0.1,
			end_price_callback=lambda order_price: order_price,
			success_check=lambda current_price, end_price: current_price < end_price
		)

	def test_single_exceptional_wide_candle(self):

		def order_function():
			upper_bound, lower_bound = UPPER_BOUND, LOWER_BOUND

			long_order = self.manager.place_order(
				account=self.account,
				instrument=self.instrument,
				units=0.1,
				price=upper_bound,
				stop_loss=lower_bound,
				order_type=TriggerOrder.Type.STOP
			)
			logger.info(f"Placed long_order@{upper_bound} with stop_loss@{lower_bound}")

			short_order = self.manager.place_order(
				account=self.account,
				instrument=self.instrument,
				units=-0.1,
				price=lower_bound,
				stop_loss=upper_bound,
				order_type=TriggerOrder.Type.STOP
			)
			logger.info(f"Placed short_order@{lower_bound} with stop_loss@{upper_bound}")

		def assert_function():
			open_trades = Trade.objects.filter(account=self.account, close_time=None)
			self.assertEqual(len(open_trades), 1)
			trade = open_trades[0]
			self.assertAlmostEqual(trade.price, LOWER_BOUND)
			self.assertAlmostEqual(trade.stop_loss, UPPER_BOUND)
			logger.info(f"Assertion Successful")
			logger.info(f"Trade(units={trade.units}, price={trade.price}, stop_loss={trade.stop_loss}, unrealize_pl={self.manager.get_unrealized_pl(trade)}) ")

		def success_function(*args, **kwargs):
			return self.repository.get_datetime() > end_time

		CONSTANT_VALUES = (1.0, 0.9998, 1.0002, 0.9999)
		EXCEPTION_VALUES = (0.9997, 0.998, 1.002, 1.0)
		PLACEMENT = 0.75
		END_PLACEMENT = 0.8
		SIZE = 12
		DELTA_MULTIPLIER = 15

		UPPER_BOUND, LOWER_BOUND = 1.001, 0.999

		self._setUp(generator=self.__create_expception_value_generator(
			constant_values=CONSTANT_VALUES,
			exception_values=EXCEPTION_VALUES,
			placement=PLACEMENT
		), size=SIZE, delta_multiplier=DELTA_MULTIPLIER)

		start_time = self.repository.get_datetime()
		end_time = start_time + timedelta(minutes=int(END_PLACEMENT*SIZE/2))
		logger.info(f"Start Time: {start_time}, End Time: {end_time}")

		self.__test_order(
			order_function=order_function,
			expected_orders=1,
			expected_trades=1,
			plot_function=lambda ax, current_price, current_time:  self.__plot_price(ax, current_price, current_time,
																					UPPER_BOUND, LOWER_BOUND),
			success_check=success_function,
			assert_function=assert_function
		)
