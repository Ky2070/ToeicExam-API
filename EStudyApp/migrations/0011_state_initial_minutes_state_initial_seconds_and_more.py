# Generated by Django 5.1.2 on 2024-12-04 15:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('EStudyApp', '0010_state_test_state_used_state_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='state',
            name='initial_minutes',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='state',
            name='initial_seconds',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='state',
            name='time',
            field=models.DurationField(blank=True, null=True),
        ),
    ]
