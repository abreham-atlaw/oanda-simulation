from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.authentication.serializers import AccountSummarySerializer


class AccountSummaryView(APIView):

	def get(self, request: Request, *args, **kwargs):
		serializer = AccountSummarySerializer(instance=request.account)
		return Response(
			data=serializer.data,
			status=status.HTTP_200_OK
		)

