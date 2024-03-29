from rest_framework import serializers

from apps.core.models import Trade
from apps.core.serializers import InstrumentSerializer


class CreateOrderRequestSerializer(serializers.Serializer):

	units = serializers.IntegerField()
	instrument = InstrumentSerializer()

	def to_internal_value(self, data):
		return super().to_internal_value(data["order"])


class CreateOrderResponseSerializer(serializers.Serializer):

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
			}
		}
