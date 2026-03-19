from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.serializers import CreateOrderRequestSerializer, CreateOrderResponseSerializer
from di.misc_provider import logger
from di.utils_provider import UtilsProvider
from utils.trading.manager import InvalidTriggerValueException


#
# @attr.define
# class Order:
#
# 	units: int = attr.ib()
# 	instrument: str = attr.ib()
# 	timeInForce: str = attr.ib()
# 	type: Optional[str] = "MARKET"
# 	positionFill: Optional[str] = "DEFAULT"
#

class CreateOrderView(APIView):

	def post(self, request: Request, *args, **kwargs):

		manager = UtilsProvider.provide_manager(request.account)

		serializer = CreateOrderRequestSerializer(data=request.data)
		serializer.is_valid(raise_exception=True)

		try:
			trade = manager.open_trade(
				request.account,
				**serializer.validated_data
			)

		except InvalidTriggerValueException as ex:
			logger.error(str(ex))
			return Response(
				status=status.HTTP_400_BAD_REQUEST,
				data={
					"orderCancelTransaction": {
						"orderID": "00",
						"reason": "INVALID_TRIGGER_VALUE"
					}
				}
			)

		serializer = CreateOrderResponseSerializer(instance=trade)
		return Response(
			data=serializer.data,
			status=status.HTTP_201_CREATED
		)
