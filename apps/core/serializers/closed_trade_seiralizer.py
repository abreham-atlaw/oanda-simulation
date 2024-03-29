from rest_framework import serializers

from apps.core.models import Trade


class ClosedTradeSerializer(serializers.Serializer):

	def to_representation(self, instance: Trade):
		return {
			"orderFillTransaction": {
				"orderID": instance.id,
				"tradesClosed": [
					{
						"tradeID": instance.id,
						"units": instance.units,
						"realizedPL": instance.realized_pl
					}
				]
			}
		}
