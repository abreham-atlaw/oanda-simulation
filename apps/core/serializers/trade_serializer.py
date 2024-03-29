#
#
# @attr.define
# class Trade:
#
# 	id: str = attr.ib()
# 	instrument: str = attr.ib()
# 	initialUnits: int = attr.ib()
# 	initialMarginRequired: float = attr.ib()
# 	realizedPL: float = attr.ib()
# 	unrealizedPL: float = attr.ib()
# 	marginUsed: float = attr.ib()
# 	state: str = attr.ib()
# 	price: float = attr.ib()
import typing

from rest_framework import serializers

from apps.core.models import Trade
from apps.core.serializers import InstrumentSerializer
from di.utils_provider import UtilsProvider


class TradeSerializer(serializers.ModelSerializer):

	class Meta:
		model = Trade
		fields = [
			"id", "instrument", "initialUnits", "initialMarginRequired",
			"realizedPL", "unrealizedPL", "marginUsed", "state", "price"
		]

	initialUnits = serializers.FloatField(source="units")
	initialMarginRequired = serializers.FloatField(source="margin_required")
	realizedPL = serializers.FloatField(source="realized_pl")
	unrealizedPL = serializers.SerializerMethodField()
	marginUsed = serializers.SerializerMethodField()
	instrument = InstrumentSerializer()

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.___manager = None

	@property
	def __manager(self):
		if self.___manager is None:
			if isinstance(self.instance, typing.Iterable):
				instance = self.instance[0]
			self.___manager = UtilsProvider.provide_manager(instance.account)
		return self.___manager

	def get_unrealizedPL(self, obj: Trade):
		return self.__manager.get_unrealized_pl(obj)

	def get_marginUsed(self, obj: Trade):
		return self.__manager.get_margin_used(obj)

