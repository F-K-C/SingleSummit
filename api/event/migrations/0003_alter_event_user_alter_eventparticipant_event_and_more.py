# Generated by Django 4.2.1 on 2023-07-09 13:44

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('event', '0002_eventparticipant'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='user',
            field=models.ForeignKey(db_column='UserId', default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='event_user', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='eventparticipant',
            name='event',
            field=models.ForeignKey(db_column='EventId', default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='event_participant', to='event.event'),
        ),
        migrations.AlterField(
            model_name='eventparticipant',
            name='user',
            field=models.ForeignKey(db_column='UserId', default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='event_participant_user', to=settings.AUTH_USER_MODEL),
        ),
    ]
