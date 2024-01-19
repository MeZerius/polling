from django.apps import AppConfig


class PollappConfig(AppConfig):
    name = 'pollApp'
    default_auto_field = 'django.db.models.BigAutoField'
    verbose_name = 'Poll Application'
    path = '/path/to/pollApp'
    label = 'poll_app'
    models_module = 'pollApp.models'
