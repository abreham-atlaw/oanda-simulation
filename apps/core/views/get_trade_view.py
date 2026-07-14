from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.models import Trade
from apps.core.serializers import TradeSerializer


class GetTradeView(APIView):

	def get(self, request: Request, *args, trade_id: str = None, **kwargs):

		trade = get_object_or_404(Trade, pk=trade_id)

		serializer = TradeSerializer(instance=trade)

		return Response(
			data={
				"trade": serializer.data,
			},
			status=status.HTTP_200_OK
		)
