from rest_framework import serializers


class PriceSerializer(serializers.Serializer):

	def to_representation(self, instance):
		if instance is None:
			return None
		return {"price": instance}

	def to_internal_value(self, data):
		if data is None:
			return None
		return data["price"]