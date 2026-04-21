from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.models import LimitOrder
from apps.core.serializers import CreateOrderResponseSerializer


class GetPendingOrdersView(APIView):

	def get(self, request: Request, *args, **kwargs) -> Response:

		instances = LimitOrder.objects.filter(account=request.account, close_time=None)
		serializer = CreateOrderResponseSerializer(many=True, instance=instances)

		return Response(
			data=serializer.data,
			status=status.HTTP_200_OK
		)
