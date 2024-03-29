from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.authentication.models import Account
from apps.core.models import Trade
from apps.core.serializers import TradeSerializer


class GetTradesView(APIView):

	def _queryset(self, account: Account):
		return Trade.objects.filter(account=account)

	def get(self, request: Request, *args, **kwargs):

		instances = self._queryset(request.account)
		serializer = TradeSerializer(instance=instances, many=True)
		return Response(
			data={
				"trades": serializer.data
			},
			status=status.HTTP_200_OK
		)


class GetOpenTradesView(GetTradesView):

	def _queryset(self, account: Account):
		return super()._queryset(account).filter(close_time=None)


class GetClosedTradesView(GetTradesView):

	def _queryset(self, account: Account):
		return super()._queryset(account).exclude(close_time=None)
