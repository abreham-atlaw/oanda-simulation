from datetime import datetime

from pytz import timezone
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.authentication.models import Account
from apps.authentication.serializers import CreateAccountSerializer, AccountSummarySerializer


class CreateAccountView(APIView):

	def post(self, request: Request) -> Response:

		serializer = CreateAccountSerializer(data=request.data)
		serializer.is_valid(raise_exception=True)

		start_time = serializer.validated_data.pop("start_time")
		time_delta = int(
			(
				datetime.now().replace(tzinfo=timezone("UTC")) - start_time
			).total_seconds()//60
		)
		account = Account.objects.create(
			**serializer.validated_data,
			time_delta=time_delta
		)

		serializer = AccountSummarySerializer(instance=account)

		return Response(
			data=serializer.data,
			status=status.HTTP_201_CREATED
		)
