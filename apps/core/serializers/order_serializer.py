import typing

from rest_framework import serializers

from apps.core.models import TriggerOrder
from apps.core.serializers import InstrumentSerializer, PriceSerializer


class OrderSerializer(serializers.Serializer):

	instrument = InstrumentSerializer()
	units = serializers.FloatField()
	takeProfitOnFill = PriceSerializer(source="take_profit")
	stopLossOnFill = PriceSerializer(source="stop_loss")
	price = serializers.DecimalField(decimal_places=5, max_digits=10)

	def to_representation(self, instance: TriggerOrder):
		data = super().to_representation(instance)

		order_type = "LIMIT" if instance.is_limit_order else "STOP"

		data.update({
			"id": str(instance.id),
			"type": order_type,
			"timeInForce": "GTC"
		})

		return data