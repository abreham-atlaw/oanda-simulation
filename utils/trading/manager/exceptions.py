


class InvalidTriggerValueException(Exception):

	def __init__(self, take_profit: float, stop_loss: float, price: float, units: float):
		super().__init__(
			f"Invalid Trigger value(s) encountered. Take Profit: {take_profit}, Stop Loss: {stop_loss}, "
			f"Price: {price}, Units: {units}"
		)
