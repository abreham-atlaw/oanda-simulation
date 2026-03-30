from datetime import datetime


class TradeException(Exception):
	pass



class InvalidTriggerValueException(TradeException):

	def __init__(self, take_profit: float, stop_loss: float, price: float, units: float):
		super().__init__(
			f"Invalid Trigger value(s) encountered. Take Profit: {take_profit}, Stop Loss: {stop_loss}, "
			f"Price: {price}, Units: {units}"
		)


class MarketClosedException(TradeException):

	def __init__(
			self,
			time: datetime
	):
		super().__init__(f"Market Closed. Now: {time.isoformat()}")
