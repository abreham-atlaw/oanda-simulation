from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.serializers import CreateOrderRequestSerializer, CreateOrderResponseSerializer
from di.misc_provider import logger
from di.utils_provider import UtilsProvider
from utils.trading.manager import InvalidTriggerValueException, MarketClosedException, TradeException


class CreateOrderView(APIView):

	__ERROR_REASON_MAP = {
		InvalidTriggerValueException.__name__: "INVALID_TRIGGER_VALUE",
		MarketClosedException.__name__: "MARKET_CLOSED"
	}

	def post(self, request: Request, *args, **kwargs):

		manager = UtilsProvider.provide_manager(request.account)

		serializer = CreateOrderRequestSerializer(data=request.data)
		serializer.is_valid(raise_exception=True)

		if serializer.validated_data.pop("type") == CreateOrderRequestSerializer.OrderTypes.limit:
			trade = manager.create_limit_order(
				request.account,
				**serializer.validated_data
			)
		else:
			try:
				trade = manager.open_trade(
					request.account,
					**serializer.validated_data
				)

			except TradeException as ex:
				logger.error(str(ex))
				return Response(
					status=status.HTTP_201_CREATED,
					data={
						"orderCancelTransaction": {
							"orderID": "00",
							"reason": self.__ERROR_REASON_MAP.get(ex.__class__.__name__)
						}
					}
				)

		serializer = CreateOrderResponseSerializer(instance=trade)
		return Response(
			data=serializer.data,
			status=status.HTTP_201_CREATED
		)
