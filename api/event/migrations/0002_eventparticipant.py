# Generated by Django 4.2.1 on 2023-07-09 13:39

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('event', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='EventParticipant',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_by', models.BigIntegerField(blank=True, db_column='CreatedBy', default=0, null=True)),
                ('created_on', models.DateTimeField(auto_now_add=True, db_column='CreatedOn')),
                ('modified_by', models.BigIntegerField(blank=True, db_column='ModifiedBy', default=0, null=True)),
                ('modified_on', models.DateTimeField(auto_now=True, db_column='ModifiedOn')),
                ('event', models.ForeignKey(db_column='EventId', default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='event.event')),
                ('user', models.ForeignKey(db_column='UserId', default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'Event_Participant',
            },
        ),
    ]
