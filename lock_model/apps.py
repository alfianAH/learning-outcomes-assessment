from django.apps import AppConfig


class LockModelConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'lock_model'

    def ready(self) -> None:
        import lock_model.signals