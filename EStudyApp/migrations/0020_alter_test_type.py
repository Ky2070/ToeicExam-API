# Generated by Django 5.1.2 on 2024-12-11 16:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('EStudyApp', '0019_alter_test_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='test',
            name='type',
            field=models.CharField(blank=True, choices=[('Online', 'Online'), ('Practice', 'Practice'), ('All', 'All')], max_length=30, null=True),
        ),
    ]
