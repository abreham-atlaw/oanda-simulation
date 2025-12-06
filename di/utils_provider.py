import os
from datetime import datetime

import pandas as pd

from Oanda import settings
from Oanda.settings import CURRENCY_DF_PATH, SPREAD_COST_PERCENTAGE, CURRENCY_DF_URL

from apps.authentication.models import Account
from di.misc_provider import logger
from utils.trading.data.repository import CurrencyRepository
from utils.trading.data.repository.dataframe_repository import DataFrameRepository
from utils.trading.manager import TradeManager, BackgroundTradeManager


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
	def __get_key(account: Account) -> str:
		return f"{account.time_delta},{account.delta_multiplier}"

	@staticmethod
	def provide_repository(account: Account) -> CurrencyRepository:

		repository = UtilsProvider.__repositories.get(UtilsProvider.__get_key(account))

		if repository is None:
			repository = DataFrameRepository(
				df=UtilsProvider.provide_df(),
				time_delta=account.time_delta,
				spread_cost_percentage=SPREAD_COST_PERCENTAGE,
				delta_multiplier=account.delta_multiplier
			)
			UtilsProvider.__repositories[UtilsProvider.__get_key(account)] = repository

		return repository

	@staticmethod
	def provide_manager(account: Account) -> TradeManager:
		key = UtilsProvider.__get_key(account)
		manager = UtilsProvider.__managers.get(key)

		if manager is None:
			manager = TradeManager(
				repository=UtilsProvider.provide_repository(account)
			)
			UtilsProvider.__managers[key] = manager
			bg_manager = UtilsProvider.provide_background_manager(manager)
			bg_manager.start()

		return manager

	@staticmethod
	def provide_background_manager(manager: TradeManager) -> BackgroundTradeManager:
		return BackgroundTradeManager(
			manager=manager,
			sleep_time=settings.BACKGROUND_MANAGER_SLEEP_TIME
		)
