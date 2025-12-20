from rest_framework import serializers

from apps.core.models import Trade
from apps.core.serializers import InstrumentSerializer
from .price_serializer import PriceSerializer


class CreateOrderRequestSerializer(serializers.Serializer):

	units = serializers.IntegerField()
	instrument = InstrumentSerializer()
	stopLossOnFill = PriceSerializer(source="stop_loss", allow_null=True, required=False)
	takeProfitOnFill= PriceSerializer(source="take_profit", allow_null=True, required=False)

	def to_internal_value(self, data):
		return super().to_internal_value(data["order"])


class CreateOrderResponseSerializer(serializers.Serializer):

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.__price_serializer = PriceSerializer(allow_null=True)

	def to_representation(self, instance: Trade):
		return {
			"orderFillTransaction": {
				"reason": "MARKET_ORDER",
				"orderID": instance.id,
				"requestedUnits": instance.units,
				"tradeOpened": {
					"tradeID": instance.id,
					"units": instance.units,
					"initialMarginRequired": instance.margin_required
				},
				"stopLossOnFill": self.__price_serializer.to_representation(instance.stop_loss),
				"takeProfitOnFill": self.__price_serializer.to_representation(instance.take_profit)
			}
		}
