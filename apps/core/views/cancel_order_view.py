from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.models import LimitOrder
from apps.core.serializers.cancel_order_serializer import CancelOrderSerializer
from di import UtilsProvider


class CancelOrderView(APIView):

	def put(self, request: Request, *args, **kwargs) -> Response:
		manager = UtilsProvider.provide_manager(request.account)

		order = get_object_or_404(LimitOrder, pk=kwargs.get("order_id"), close_time=None)
		manager.cancel_order(order)

		serializer = CancelOrderSerializer(instance=order)

		return Response(
			data=serializer.data,
			status=status.HTTP_200_OK
		)
