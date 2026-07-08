from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.models import TriggerOrder
from apps.core.serializers import OrderSerializer


class GetOrderView(APIView):

	def get(self, *args, order_id: str, **kwargs):

		order = get_object_or_404(TriggerOrder, pk=order_id)

		serializer = OrderSerializer(instance=order)

		return Response(
			data=serializer.data,
			status=status.HTTP_200_OK
		)
