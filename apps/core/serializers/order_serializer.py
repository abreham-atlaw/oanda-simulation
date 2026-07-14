import typing

from rest_framework import serializers

from apps.core.models import TriggerOrder, Trade
from apps.core.serializers import InstrumentSerializer, PriceSerializer


class OrderSerializer(serializers.Serializer):

	instrument = InstrumentSerializer()
	units = serializers.FloatField()
	takeProfitOnFill = PriceSerializer(source="take_profit")
	stopLossOnFill = PriceSerializer(source="stop_loss")
	price = serializers.DecimalField(decimal_places=5, max_digits=10)
	state = serializers.CharField()
	tradeOpenedID = serializers.PrimaryKeyRelatedField(allow_null=True, queryset=Trade.objects.all(), source="trade_opened")

	def __get_order_type(self, instance: TriggerOrder) -> str:
		if not instance.is_trade_related:
			if instance.is_limit_order:
				return "LIMIT"
			return "STOP"
		if instance.is_limit_order:
			return "TAKE_PROFIT"
		return "STOP_LOSS"

	def to_representation(self, instance: TriggerOrder):
		data = super().to_representation(instance)

		order_type = self.__get_order_type(instance)

		data.update({
			"id": str(instance.id),
			"type": order_type,
			"timeInForce": "GTC"
		})

		return data