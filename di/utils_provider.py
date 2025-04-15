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
		parent = os.path.dirname(CURRENCY_DF_PATH)
		if not os.path.exists(parent):
			os.makedirs(parent)
		print("Downloading DF...")
		os.system(f"wget --no-verbose \"{CURRENCY_DF_URL}\" -O \"{CURRENCY_DF_PATH}\"")

	@staticmethod
	def provide_df() -> pd.DataFrame:
		if os.path.exists(CURRENCY_DF_PATH):
			return pd.read_csv(CURRENCY_DF_PATH)
		UtilsProvider.__download_df()
		return UtilsProvider.provide_df()


	@staticmethod
	def provide_repository(account: Account) -> CurrencyRepository:

		def __get_key(account: Account) -> str:
			return f"{account.time_delta},{account.delta_multiplier}"

		repository = UtilsProvider.__repositories.get(__get_key(account))

		if repository is None:
			repository = DataFrameRepository(
				df=UtilsProvider.provide_df(),
				time_delta=account.time_delta,
				spread_cost_percentage=SPREAD_COST_PERCENTAGE,
				delta_multiplier=account.delta_multiplier
			)
			UtilsProvider.__repositories[__get_key(account)] = repository

		return repository

	@staticmethod
	def provide_manager(account: Account) -> TradeManager:
		time_delta = account.time_delta
		manager = UtilsProvider.__managers.get(time_delta)

		if manager is None:
			manager = TradeManager(
				repository=UtilsProvider.provide_repository(account)
			)
			UtilsProvider.__managers[f"{account.time_delta},{account.delta_multiplier}"] = manager

		return manager
