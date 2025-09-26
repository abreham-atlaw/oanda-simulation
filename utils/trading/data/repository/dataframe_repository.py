from datetime import datetime, timedelta

import pandas as pd
from typing import List

from pytz import timezone

from utils.cache.decorators import CacheDecorators
from utils.devtools import stats
from utils.trading.data.models import Instrument, Candlestick
from utils.trading.data.repository import CurrencyRepository


class DataFrameRepository(CurrencyRepository):

	def __init__(
			self,
			df: pd.DataFrame,
			time_delta: int,
			spread_cost_percentage: float,
			delta_multiplier: float = 1,
			min_granularity=1
	):
		self.df = self.__prepare_df(df)
		self.__timedelta = timedelta(minutes=time_delta)
		self.__spread_cost = spread_cost_percentage
		self.__delta_multiplier = delta_multiplier
		self.__start_datetime = self.__translate_time(datetime.now(), multiply=False)
		self.__min_granularity = min_granularity

	@staticmethod
	def __prepare_df(df: pd.DataFrame) -> pd.DataFrame:
		df["time"] = pd.to_datetime(df["time"])
		df = df.drop_duplicates(subset="time")
		df = df.sort_values(by="time")
		return df

	@property
	def __current_datetime(self) -> datetime:
		return self.__translate_time(datetime.now())

	def __translate_time(self, date, multiply=True) -> datetime:
		if date.tzinfo is None:
			date = date.replace(tzinfo=timezone("UTC"))
		date = date - self.__timedelta

		if multiply:
			date = self.__start_datetime + (date - self.__start_datetime) * self.__delta_multiplier
		print(date)

		return date

	@staticmethod
	def __round_time(date: datetime, gran: int) -> datetime:
		return date.replace(minute=(date.minute // gran) * gran, second=0, microsecond=0)

	@stats.track_func(key="DataFrameRepository.__get_instrument_df")
	@CacheDecorators.cached_method()
	def __get_instrument_df(self, instrument: Instrument) -> pd.DataFrame:
		instrument_df = self.df[
			(self.df['base_currency'] == instrument[0]) &
			(self.df['quote_currency'] == instrument[1])
			]
		if instrument_df.shape[0] == 0:
			instrument = instrument[1], instrument[0]
			instrument_df = self.__get_instrument_df(instrument).copy()
			for col in ["o", "h", "l", "c"]:
				instrument_df[col] = 1 / instrument_df[col]
			instrument_df["base_currency"], instrument_df["quote_currency"] = instrument[::-1]

		return instrument_df

	@stats.track_func(key="DataframeRepository.__filter_df")
	def __filter_df(self, instrument: Instrument = None, time: datetime = None):
		df = self.df
		if instrument is not None:
			df = self.__get_instrument_df(instrument)
		if time is not None:
			df = df[df["time"] <= time]
		return df

	@stats.track_func(key="DataFrameRepository.get_instruments")
	def get_instruments(self) -> List[Instrument]:
		return list(set(self.df[['base_currency', 'quote_currency']].itertuples(index=False, name=None)))

	@stats.track_func(key="DataFrameRepository.get_price")
	def get_price(self, instrument: Instrument) -> float:
		if instrument[0] == instrument[1]:
			return 1.0
		df = self.__filter_df(instrument=instrument, time=self.__current_datetime)
		return df['c'].iloc[-1]

	@stats.track_func(key="DataFrameRepository.get_spread_cost")
	def get_spread_cost(self, instrument: Instrument, price: float = None) -> float:
		if price is None:
			price = self.get_price(instrument)
		return price * self.__spread_cost

	@stats.track_func(key="DataFrameRepository.get_candlestick")
	def get_candlestick(self, instrument: Instrument, granularity: int, count: int, to: datetime) -> List[Candlestick]:
		instrument_df = self.__filter_df(
			instrument=instrument,
			time=self.__round_time(self.__translate_time(to), gran=granularity)
		)
		instrument_df = instrument_df.iloc[-count * granularity::granularity]

		if instrument_df.shape[0] < count:
			raise ValueError("Not enough data")

		return [
			Candlestick(row['v'], row['o'], row['c'], row['h'], row['l'], row['time'])
			for _, row in instrument_df.iterrows()
		]

	def get_datetime(self) -> datetime:
		return self.__translate_time(super().get_datetime())
