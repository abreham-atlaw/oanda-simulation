import logging

from Oanda import settings


class MiscProvider:

	@staticmethod
	def provide_logger():
		return logging.getLogger(settings.DEFAULT_LOGGING_ID)


logger = MiscProvider.provide_logger()