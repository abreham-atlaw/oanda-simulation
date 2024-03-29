from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.serializers import CreateOrderRequestSerializer, CreateOrderResponseSerializer
from di.utils_provider import UtilsProvider


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

		trade = manager.open_trade(
			request.account,
			**serializer.validated_data
		)

		serializer = CreateOrderResponseSerializer(instance=trade)
		return Response(
			data=serializer.data,
			status=status.HTTP_201_CREATED
		)
