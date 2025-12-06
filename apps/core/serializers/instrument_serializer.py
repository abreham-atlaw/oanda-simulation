from django.core.exceptions import ValidationError
from rest_framework import serializers

from Oanda import settings


class InstrumentSerializer(serializers.Serializer):

	def to_internal_value(self, data):
		if "/" in data:
			delimiter = "/"
		elif "_" in data:
			delimiter = "_"
		else:
			raise ValidationError("Invalid Instrument")
		return tuple(data.split(delimiter))

	def to_representation(self, instance):
		return "_".join(instance)


class FullInstrumentSerializer(InstrumentSerializer):

	def to_representation(self, instance):
		return {
			"name": super().to_representation(instance),
			"displayPrecision": settings.INSTRUMENT_DISPLAY_PRECISION[instance]
		}
