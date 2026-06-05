from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.models import TriggerOrder
from apps.core.serializers import CreateOrderResponseSerializer, OrderSerializer


class GetPendingOrdersView(APIView):

	def get(self, request: Request, *args, **kwargs) -> Response:

		orders = TriggerOrder.objects.filter(account=request.account, close_time=None, trade=None)
		serializer = OrderSerializer(many=True, instance=orders)

		return Response(
			data={
				"orders": serializer.data
			},
			status=status.HTTP_200_OK
		)
