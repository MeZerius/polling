from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


class Poll(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=200)
    quorum = models.IntegerField()
    active_time = models.DurationField()
    created_at = models.DateTimeField(default=timezone.now)

    @property
    def is_expired(self):
        return timezone.now() > self.created_at + self.active_time

    @property
    def is_invalid(self):
        if not self.is_expired:
            return None
        return self.options.aggregate(models.Sum('votes__count'))['votes__count__sum'] < self.quorum

    def clean(self):
        if self.quorum < 2:
            raise ValidationError('Quorum cannot be less than 2.')

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
