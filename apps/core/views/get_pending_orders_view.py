from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.models import LimitOrder, StopOrder
from apps.core.serializers import CreateOrderResponseSerializer, OrderSerializer


class GetPendingOrdersView(APIView):

	def get(self, request: Request, *args, **kwargs) -> Response:

		limit_orders = LimitOrder.objects.filter(account=request.account, close_time=None)
		stop_order = StopOrder.objects.filter(account=request.account, close_time=None)
		orders = list(limit_orders) + list(stop_order)
		serializer = OrderSerializer(many=True, instance=orders)

		return Response(
			data={
				"orders": serializer.data
			},
			status=status.HTTP_200_OK
		)
