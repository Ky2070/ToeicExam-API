# Generated by Django 5.1.2 on 2024-12-11 15:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('EStudyApp', '0015_state_updated_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='state',
            name='time_taken',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
