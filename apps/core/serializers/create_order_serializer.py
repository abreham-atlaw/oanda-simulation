import typing

from rest_framework import serializers

from apps.core.models import Trade, LimitOrder
from apps.core.serializers import InstrumentSerializer
from .price_serializer import PriceSerializer


class CreateOrderRequestSerializer(serializers.Serializer):

	class OrderTypes:
		market = "MARKET",
		limit = "LIMIT"
		all = [market, limit]

	units = serializers.FloatField()
	instrument = InstrumentSerializer()
	stopLossOnFill = PriceSerializer(source="stop_loss", allow_null=True, required=False)
	takeProfitOnFill= PriceSerializer(source="take_profit", allow_null=True, required=False)
	type = serializers.ChoiceField(choices=[(c, c) for c in OrderTypes.all])
	price = serializers.DecimalField(max_digits=8, decimal_places=5, allow_null=True, required=False)

	def to_internal_value(self, data):
		return super().to_internal_value(data["order"])


class CreateOrderResponseSerializer(serializers.Serializer):

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.__price_serializer = PriceSerializer(allow_null=True)

	def to_representation(self, instance: typing.Union[Trade, LimitOrder]):

		is_trade = isinstance(instance, Trade)

		rep = {
			"orderCreateTransaction": {
				"reason": "MARKET_ORDER" if is_trade else "CLIENT_ORDER",
				"orderID": instance.id,
				"requestedUnits": instance.units,
				"type": "MARKET_ORDER" if is_trade else "LIMIT_ORDER",

				"stopLossOnFill": self.__price_serializer.to_representation(instance.stop_loss),
				"takeProfitOnFill": self.__price_serializer.to_representation(instance.take_profit)
			}
		}
		if is_trade:
			rep["tradeOpened"] = {
				"tradeID": instance.id,
				"units": instance.units,
				"initialMarginRequired": instance.margin_required
			}
		return rep
