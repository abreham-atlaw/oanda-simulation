from rest_framework import serializers
from apps.authentication.models import Account
from di.utils_provider import UtilsProvider


class AccountSummarySerializer(serializers.ModelSerializer):

	class Meta:
		model = Account
		fields = ["NAV", "alias", "balance", "currency", "id", "marginAvailable", "marginRate", "marginUsed"]

	NAV = serializers.SerializerMethodField()
	marginAvailable = serializers.SerializerMethodField()
	marginRate = serializers.FloatField(source="margin_rate")
	marginUsed = serializers.SerializerMethodField()

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.__manager = UtilsProvider.provide_manager(self.instance)

	def to_representation(self, instance):
		return {
			"account": super().to_representation(instance)
		}

	def get_NAV(self, obj):
		return self.__manager.get_nav(obj)

	def get_marginAvailable(self, obj):
		return self.__manager.get_margin_available(obj)

	def get_marginUsed(self, obj):
		return self.__manager.get_account_margin_used(obj)
