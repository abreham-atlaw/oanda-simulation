from rest_framework import serializers

from datetime import datetime

from utils.trading.data.models import Candlestick


class GranularitySerializer(serializers.Field):

	def to_internal_value(self, data):
		return {
			"H5": 5*60,
			"H1": 1*60,
			"M5": 5,
			"M1": 1,
		}[data]


class CustomDateTimeField(serializers.Field):

	def to_representation(self, value):
		return value.strftime('%Y-%m-%dT%H:%M:%S.%f') + 'Z'


class CandlestickSerializer(serializers.Serializer):

	def to_representation(self, instance: Candlestick):
		__datetime_serializer = CustomDateTimeField()

		return {
			"complete": True,
			"volume": instance.volume,
			"time": __datetime_serializer.to_representation(instance.time),
			"mid": {
				"o": instance.open,
				"h": instance.high,
				"l": instance.low,
				"c": instance.close
			}
		}

