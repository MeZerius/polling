from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


class Poll(models.Model):
    QUORUM_TYPE_CHOICES = [
        ('P', 'Percent'),
        ('N', 'Number'),
        ('D', 'Disabled'),
    ]
    TIME_OPTION_CHOICES = [
        ('A', 'Active Time'),
        ('E', 'End Time'),
    ]

    START_OPTION_CHOICES = [
        ('S', 'Start Time'),
        ('I', 'Immediately'),
    ]

    id = models.AutoField(primary_key=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='polls')
    title = models.CharField(max_length=200)
    majority = models.BooleanField(default=False)
    quorum = models.IntegerField(null=True, blank=True)
    quorum_type = models.CharField(max_length=1, choices=QUORUM_TYPE_CHOICES, default='N')
    active_time = models.DurationField(help_text="Enter the active time for the poll in the format: DD HH:MM:SS.", null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    start_time = models.DateTimeField(default=timezone.now, null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    time_option = models.CharField(max_length=1, choices=TIME_OPTION_CHOICES, default='A')
    start_option = models.CharField(max_length=1, choices=START_OPTION_CHOICES, default='I')


    @property
    def quorum_number(self):
        if self.quorum is None:
            return None
        if self.quorum_type == 'P':
            return int(User.objects.count() * self.quorum / 100)
        else:
            return self.quorum

    @property
    def is_expired(self):
        if self.end_time:
            return timezone.now() > self.end_time
        elif self.start_time and self.active_time:
            return timezone.now() > self.start_time + self.active_time
        elif self.active_time:
            return timezone.now() > self.created_at + self.active_time
        else:
            return False

    @property
    def is_invalid(self):
        if not self.is_expired or self.quorum is None:
            return None
        total_votes = sum(option.votes.count() for option in self.options.all())
        if self.quorum_type == 'P':
            return total_votes < (User.objects.count() * self.quorum / 100)
        else:
            return total_votes < self.quorum

    def has_user_voted(self, user):
        return self.options.filter(votes=user).exists()

    def clean(self):
        if  self.quorum_type == 'D' and self.quorum is not None:
            raise ValidationError('Quorum must be empty when Quorum Type is set to Disabled')
        if self.quorum_type != 'D' and self.quorum is None:
            raise ValidationError('Quorum must be filled out when Quorum Type is not set to Disabled')

        if self.title is None or self.quorum_type is None:
            raise ValidationError('Title and Quorum Type fields must be filled out')

        if self.quorum is not None:
            if self.quorum_type == 'P':
                if not 0 <= self.quorum <= 100:
                    raise ValidationError('Quorum must be between 0 and 100 when Quorum Type is set to Percent')
            else:
                if self.quorum < 2:
                    raise ValidationError('Quorum must be greater than or equal to 2 when Quorum Type is set to Number')

        if self.time_option == 'A':
            if self.active_time is None:
                raise ValidationError('Active time must be filled out when Time Option is set to Active Time')
            if self.active_time.total_seconds() <= 0:
                raise ValidationError('Active time cannot be zero or less.')
            if self.end_time:
                raise ValidationError('You cannot set both end time and active time.')

        if self.time_option == 'E' and self.end_time is None:
            raise ValidationError('End time must be filled out when Time Option is set to End Time')

        if self.start_option == 'S' and self.start_time is None:
            raise ValidationError('Start time must be filled out when Start Option is set to Start Time')

        if self.active_time and self.active_time.total_seconds() <= 0:
            raise ValidationError('Active time cannot be zero or less.')

        if self.end_time and self.active_time:
            raise ValidationError('You cannot set both end time and active time.')

        if self.end_time and self.start_time and self.end_time < self.start_time:
            raise ValidationError('End time cannot be before start time.')

        def save(self, *args, **kwargs):
            if self.start_time is None:
                self.start_time = timezone.now()
            if self.time_option == 'E' and self.end_time is not None:
                self.active_time = None
            super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class Option(models.Model):
    id = models.AutoField(primary_key=True)
    poll = models.ForeignKey(Poll, related_name='options', on_delete=models.CASCADE)
    text = models.CharField(max_length=200)
    votes = models.ManyToManyField(User, related_name='votes', blank=True)

    def vote(self, user):
        has_voted = any(user in option.votes.all() for option in self.poll.options.all())
        if not has_voted:
            self.votes.add(user)

    def __str__(self):
        return self.text