from django.apps import AppConfig


class LogtailerConfig(AppConfig):
    name = 'logtailer'
    verbose_name = "Logtailer"
    # Keep the AutoField pks from the shipped migrations regardless of the
    # host project's DEFAULT_AUTO_FIELD (avoids spurious makemigrations).
    default_auto_field = 'django.db.models.AutoField'
