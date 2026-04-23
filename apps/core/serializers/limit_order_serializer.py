from rest_framework import serializers

from apps.core.models import LimitOrder
from apps.core.serializers import InstrumentSerializer, PriceSerializer


class LimitOrderSerializer(serializers.Serializer):

	instrument = InstrumentSerializer()
	units = serializers.FloatField()
	takeProfitOnFill = PriceSerializer(source="take_profit")
	stopLossOnFill = PriceSerializer(source="stop_loss")
	price = serializers.DecimalField(decimal_places=5, max_digits=10)

	def to_representation(self, instance: LimitOrder):
		data = super().to_representation(instance)

		data.update({
			"id": str(instance.id),
			"type": "LIMIT",
			"timeInForce": "GTC"
		})

		return data