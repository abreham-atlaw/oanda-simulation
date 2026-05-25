import typing

from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.models import LimitOrder, StopOrder
from apps.core.serializers.cancel_order_serializer import CancelOrderSerializer
from di import UtilsProvider


class CancelOrderView(APIView):

	@staticmethod
	def __get_order(order_id: str) -> typing.Union[LimitOrder, StopOrder]:
		limit_order = LimitOrder.objects.filter(id=order_id, close_time=None)
		if limit_order.exists():
			return limit_order.first()
		return get_object_or_404(StopOrder, pk=order_id, close_time=None)

	def put(self, request: Request, *args, **kwargs) -> Response:
		manager = UtilsProvider.provide_manager(request.account)

		order = self.__get_order(kwargs.get("order_id"))
		manager.cancel_order(order)

		serializer = CancelOrderSerializer(instance=order)

		return Response(
			data=serializer.data,
			status=status.HTTP_200_OK
		)
