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

		bid_price, ask_price = repository.get_bid_ask_pair(serializer.validated_data)

		return Response(
			data={
				"prices": [
					{
						"closeoutBid": bid_price,
						"closeoutAsk": ask_price,
						"instrument": instrument,
						"bids": [
							{
								"price": bid_price,
								"liquidity": 500000
							}
						],
						"asks": [
							{
								"price": ask_price,
								"liquidity": 500000
							}
						]
					}
				]
			}
		)
