from django.apps import AppConfig


class EstudyappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'EStudyApp'

    def ready(self):
        import EStudyApp.signals