from django.shortcuts import get_object_or_404
from django.utils.deprecation import MiddlewareMixin
from rest_framework.request import Request

from Oanda.settings import ACCOUNT_ID_KEY
from apps.authentication.models import Account


class AccountIdMiddleware(MiddlewareMixin):

    def process_view(self, request, view_func, view_args, view_kwargs):
        id = view_kwargs.get(ACCOUNT_ID_KEY)
        if id:
            request.account = get_object_or_404(Account, pk=id)
