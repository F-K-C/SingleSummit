from django.db import models

from api.users.models import User
from main.models import Log


# Create your models here.


# Create your models here.
class Event(Log):
    """ Role model."""
    user = models.ForeignKey(
        User,
        db_column="UserId",
        related_name="event_user",
        null=True,
        default=None,
        on_delete=models.CASCADE
    )
    name = models.CharField(db_column="Name", default=None, blank=None, max_length=255)
    local = models.CharField(db_column="Local", default=None, blank=None, max_length=255)
    price = models.FloatField(db_column="Price", default=0)
    city = models.CharField(db_column="City", default=None, blank=None, max_length=255)
    type = models.CharField(db_column="Type", default=None, blank=None, max_length=255)
    description = models.TextField(db_column="Description", default=None, blank=True, null=True)
    date = models.DateTimeField(db_column="Date", default=None, null=True)

    class Meta:
        db_table = 'Event'

    def __str__(self):
        return f'{self.name}'


class EventParticipant(Log):
    """ EventParticipant model."""
    user = models.ForeignKey(
        User,
        db_column="UserId",
        related_name="event_participant_user",
        null=True,
        default=None,
        on_delete=models.CASCADE
    )
    event = models.ForeignKey(
        Event,
        db_column="EventId",
        related_name="event_participant",
        null=True,
        default=None,
        on_delete=models.CASCADE
    )
    grade = models.IntegerField(db_column="Grade", default=0, null=True)

    class Meta:
        db_table = 'Event_Participant'

    def __str__(self):
        return f'{self.name}'
