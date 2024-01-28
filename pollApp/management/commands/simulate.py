from django.contrib.auth.models import Permission, User, Group
from django.contrib.contenttypes.models import ContentType
from django.core.management import BaseCommand
from django.db import transaction
from django.utils import timezone
from pollApp.models import Poll, Option
import random

from datetime import timedelta


class Command(BaseCommand):
    help = 'Simulates the polling application by generating random data'

    @transaction.atomic
    def handle(self, *args, **options):
        # Delete all polls and users except the superadmin
        User.objects.exclude(is_superuser=True).delete()
        Poll.objects.all().delete()

        # Generate random users
        for i in range(100):
            print("User: " + str(i))
            User.objects.create_user(f'user{i}', f'user{i}@example.com', 'password')

        # Generate random secretaries
        secretary_group, _ = Group.objects.get_or_create(name='secretary')
        users = User.objects.all()
        for user in random.sample(list(users), 10):  # Adjust the number of secretaries as needed
            user.groups.add(secretary_group)

        # Assign CRUD permissions for polls to the secretary group
        poll_content_type = ContentType.objects.get_for_model(Poll)
        permissions = Permission.objects.filter(content_type=poll_content_type)
        secretary_group.permissions.set(permissions)

        # Get all secretaries
        secretaries = User.objects.filter(groups__name='secretary')

        # Generate random polls and options
        for i in range(50):
            print("Poll: " + str(i))
            poll_status = random.choice(['active', 'expired', 'upcoming'])
            if poll_status == 'expired':
                start_time = timezone.now() - timedelta(days=random.randint(30, 60))  # Start time in the past
                end_time = timezone.now() - timedelta(days=random.randint(1, 29))  # End time in the past
            elif poll_status == 'upcoming':
                start_time = timezone.now() + timedelta(days=random.randint(30, 60))  # Start time in the future
                end_time = start_time + timedelta(days=random.randint(1, 30))  # End time in the future
            else:  # active
                start_time = timezone.now() - timedelta(days=random.randint(1, 29))  # Start time in the past
                end_time = timezone.now() + timedelta(days=random.randint(1, 30))  # End time in the future

            # Randomly decide whether to set a quorum or not
            has_quorum = random.choice([True, False])
            if has_quorum:
                quorum = random.randint(1, 100)
                quorum_type = random.choice(['P', 'N'])
            else:
                quorum = None
                quorum_type = 'D'

            poll = Poll.objects.create(
                creator=random.choice(secretaries),  # Select a secretary as the creator
                title=f'Poll {i}',
                majority=random.choice([True, False]),
                quorum=quorum,
                quorum_type=quorum_type,
                active_time=timedelta(days=random.randint(1, 100)),  # Use timedelta here
                start_time=start_time,
                end_time=end_time,
                time_option=random.choice(['A', 'E']),
                start_option=random.choice(['S', 'I']),
            )

            # Generate random options for the poll
            for j in range(random.randint(2, 5)):
                print("Poll: " + str(i) + "; Vote: "+ str(j) + ";")
                Option.objects.create(
                    poll=poll,
                    text=f'Option {j}',
                )

            # Randomly assign a subset of users to vote for one option in each poll
            # Skip voting process for upcoming polls
            if poll_status != 'upcoming':
                for user in random.sample(list(users), random.randint(1, len(users))):
                    option = random.choice(poll.options.all())
                    if not poll.has_user_voted(user):
                        option.vote(user)