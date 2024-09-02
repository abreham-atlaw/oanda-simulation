import os

from django.apps import AppConfig

from Oanda.settings import LOCAL_DEFAULT_ACCOUNT_TIME_DELTA, LOCAL_DEFAULT_ACCOUNT_DELTA_MULTIPLIER, \
    LOCAL_DEFAULT_ACCOUNT_ENV_KEY, LOCAL_DEFAULT_ACCOUNT_BALANCE, CREATE_LOCAL_ACCOUNT


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
            detla_multiplier=LOCAL_DEFAULT_ACCOUNT_DELTA_MULTIPLIER
        )
        os.environ[LOCAL_DEFAULT_ACCOUNT_ENV_KEY] = str(account.id)
        print(f"Created Account {account.id}({account.alias})")
        print(os.environ)

    def ready(self):
        if CREATE_LOCAL_ACCOUNT:
            try:
                self.__create_local_account()
            except Exception as e:
                print(f"Failed to create Local Account: {e}")
