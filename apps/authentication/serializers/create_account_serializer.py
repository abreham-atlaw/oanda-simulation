from rest_framework import serializers

from apps.authentication.models import Account


class CreateAccountSerializer(serializers.ModelSerializer):

	start_time = serializers.DateTimeField()

	class Meta:
		model = Account
		fields = ["balance", "alias", "margin_rate", "delta_multiplier", "start_time"]
