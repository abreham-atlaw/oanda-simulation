from rest_framework import serializers

from apps.core.models import LimitOrder


class CancelOrderSerializer(serializers.Serializer):

	def to_representation(self, instance: LimitOrder):
		return {
			"orderCancelTransaction": {
				"id": str(instance.id),
				"accountID": instance.account.id,
				"type": "ORDER_CANCEL",
				"orderID": str(instance.id),
				"reason": "CLIENT_REQUEST"
			}
		}