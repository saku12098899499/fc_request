from django.apps import AppConfig


class FcRequestConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'fc_request'

    def ready(self):
        from .auto_task import start
        start()