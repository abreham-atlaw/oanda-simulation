from datetime import datetime

from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.serializers import InstrumentSerializer, GranularitySerializer, CandlestickSerializer
from di.utils_provider import UtilsProvider
from utils.trading.data.models import Instrument


class GetCandlestickView(APIView):

	def __get_instrument(self, data) -> Instrument:
		serializer = InstrumentSerializer(data=data)
		serializer.is_valid(raise_exception=True)
		return serializer.validated_data

	def __get_datetime(self, data) -> datetime:
		return datetime.fromtimestamp(float(data))

	def __get_granularity(self, data) -> int:
		serializer = GranularitySerializer()
		return serializer.to_internal_value(data)

	def get(self, request: Request, *args, **kwargs):

		instrument = self.__get_instrument(kwargs.get("instrument"))
		to = self.__get_datetime(request.query_params.get("to"))
		count = int(request.query_params.get("count"))
		granularity = self.__get_granularity(request.query_params.get("granularity"))

		repository = UtilsProvider.provide_repository(request.account.time_delta)

		candlestick = repository.get_candlestick(
			granularity=granularity,
			count=count,
			to=to,
			instrument=instrument
		)

		serializer = CandlestickSerializer(instance=candlestick, many=True)
		return Response(
			data={"candles": serializer.data},
			status=status.HTTP_200_OK
		)
