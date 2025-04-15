import json
import os

from django.apps import AppConfig

from Oanda.settings import LOCAL_DEFAULT_ACCOUNT_TIME_DELTA, LOCAL_DEFAULT_ACCOUNT_DELTA_MULTIPLIER, \
    LOCAL_DEFAULT_ACCOUNT_BALANCE, CREATE_LOCAL_ACCOUNT, LOCAL_DEFAULT_ACCOUNT_FILE_PATH, START_TIME_FILE_PATH, \
    LOCAL_DEFAULT_ACCOUNT_START_TIME


class AuthenticationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.authentication'

    @staticmethod
    def __create_local_account():
        print(f"Creating Local Account...")
        from apps.authentication.models import Account
        account = Account.objects.create(
            alias=f"Local Account {len(Account.objects.all())}",
            currency="USD",
            margin_rate=0.1,
            balance=LOCAL_DEFAULT_ACCOUNT_BALANCE,
            time_delta=LOCAL_DEFAULT_ACCOUNT_TIME_DELTA,
            delta_multiplier=LOCAL_DEFAULT_ACCOUNT_DELTA_MULTIPLIER
        )
        print(f"Created Account {account.id}({account.alias})")
        with open(LOCAL_DEFAULT_ACCOUNT_FILE_PATH, "w") as f:
            json.dump(str(account.id), f)

        with open(START_TIME_FILE_PATH, "w") as f:
            json.dump(str(LOCAL_DEFAULT_ACCOUNT_START_TIME), f)

    def ready(self):
        if CREATE_LOCAL_ACCOUNT:
            try:
                self.__create_local_account()
            except Exception as e:
                print(f"Failed to create Local Account: {e}")
