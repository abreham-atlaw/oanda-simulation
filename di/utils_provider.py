import os
from datetime import datetime

import pandas as pd

from Oanda.settings import CURRENCY_DF_PATH, SPREAD_COST_PERCENTAGE, CURRENCY_DF_URL

from apps.authentication.models import Account
from utils.trading.data.repository import CurrencyRepository
from utils.trading.data.repository.dataframe_repository import DataFrameRepository
from utils.trading.manager import TradeManager


class UtilsProvider:

	__repositories = {}
	__managers = {}
	__df = None

	@staticmethod
	def __download_df():
		print("Downloading DF...")
		os.system(f"wget --no-verbose \"{CURRENCY_DF_URL}\" -O \"{CURRENCY_DF_PATH}\"")

	@staticmethod
	def provide_df() -> pd.DataFrame:
		if os.path.exists(CURRENCY_DF_PATH):
			return pd.read_csv(CURRENCY_DF_PATH)
		UtilsProvider.__download_df()
		return UtilsProvider.provide_df()


	@staticmethod
	def provide_repository(time_delta: int) -> CurrencyRepository:
		repository = UtilsProvider.__repositories.get(time_delta)

		if repository is None:
			repository = DataFrameRepository(
				df=UtilsProvider.provide_df(),
				time_delta=time_delta,
				spread_cost_percentage=SPREAD_COST_PERCENTAGE
			)
			UtilsProvider.__repositories[time_delta] = repository

		return repository

	@staticmethod
	def provide_manager(account: Account) -> TradeManager:
		time_delta = account.time_delta
		manager = UtilsProvider.__managers.get(time_delta)

		if manager is None:
			manager = TradeManager(
				repository=UtilsProvider.provide_repository(time_delta)
			)
			UtilsProvider.__managers[time_delta] = manager

		return manager

