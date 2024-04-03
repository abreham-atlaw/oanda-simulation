from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.serializers import InstrumentSerializer
from di.utils_provider import UtilsProvider


class GetPricingView(APIView):

	def get(self, request: Request, *args, **kwargs):
		repository = UtilsProvider.provide_repository(request.account)
		instrument = request.query_params.get("instruments")
		serializer = InstrumentSerializer(data=instrument)
		serializer.is_valid(raise_exception=True)

		return Response(
			data={
				"prices": [
					{
						"closeoutBid": repository.get_bid_price(serializer.validated_data),
						"closeoutAsk": repository.get_ask_price(serializer.validated_data),
						"instrument": instrument
					}
				]
			}
		)
