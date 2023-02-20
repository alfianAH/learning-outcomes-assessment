from django.apps import AppConfig


class CloConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'clo'

    def ready(self) -> None:
        import clo.signals
