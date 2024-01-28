from django.core.management.commands.migrate import Command as MigrateCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from pollApp.models import Poll


class Command(MigrateCommand):
    def handle(self, *args, **kwargs):
        super().handle(*args, **kwargs)

        secretary_group, created = Group.objects.get_or_create(name='secretary')
        if created:
            poll_content_type = ContentType.objects.get_for_model(Poll)
            permissions = Permission.objects.filter(content_type=poll_content_type)
            secretary_group.permissions.set(permissions)
