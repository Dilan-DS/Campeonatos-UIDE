from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "core"

    def ready(self):
        # Registra las senales al arrancar la aplicacion. Sin esto el avance
        # automatico del cuadro de eliminatoria no se conectaria nunca.
        from core import signals  # noqa: F401
