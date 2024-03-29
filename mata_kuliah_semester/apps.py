from django.apps import AppConfig


class MataKuliahConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'mata_kuliah_semester'

    def ready(self) -> None:
        import mata_kuliah_semester.signals
