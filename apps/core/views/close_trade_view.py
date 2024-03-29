from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.models import Trade
from apps.core.serializers import ClosedTradeSerializer
from di.utils_provider import UtilsProvider


class CloseTradeView(APIView):

	def put(self, request: Request, *args, **kwargs):
		manager = UtilsProvider.provide_manager(request.account)

		trade = get_object_or_404(Trade, pk=kwargs.get("trade_id"), close_time=None)
		manager.close_trade(trade)

		serializer = ClosedTradeSerializer(instance=trade)
		return Response(
			data=serializer.data,
			status=status.HTTP_200_OK
		)
