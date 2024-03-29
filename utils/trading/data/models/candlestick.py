from dataclasses import dataclass
from datetime import datetime


@dataclass
class Candlestick:

	volume: float
	open: float
	close: float
	high: float
	low: float
	time: datetime
