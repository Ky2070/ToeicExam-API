# Generated by Django 5.1.2 on 2024-12-11 16:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('EStudyApp', '0016_state_time_taken'),
    ]

    operations = [
        migrations.AlterField(
            model_name='test',
            name='type',
            field=models.CharField(blank=True, choices=[('ONLINE', 'Test'), ('PRACTICE', 'Practice'), ('ALL', 'All')], max_length=30, null=True),
        ),
    ]