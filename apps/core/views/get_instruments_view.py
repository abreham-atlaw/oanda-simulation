from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.serializers import InstrumentSerializer, FullInstrumentSerializer
from di.utils_provider import UtilsProvider


class GetInstrumentsView(APIView):

	def get(self, request, *args, **kwargs):
		repository = UtilsProvider.provide_repository(request.account)
		instruments = repository.get_instruments()

		serializer = FullInstrumentSerializer(instance=instruments, many=True)

		return Response(
			data={
				"instruments": serializer.data
			},
			status=status.HTTP_200_OK
		)
