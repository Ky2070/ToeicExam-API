# Generated by Django 5.1.2 on 2025-03-15 09:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('EStudyApp', '0034_test_closedate_test_publishdate'),
    ]

    operations = [
        migrations.RenameField(
            model_name='test',
            old_name='closeDate',
            new_name='close_date',
        ),
        migrations.RenameField(
            model_name='test',
            old_name='publishDate',
            new_name='publish_date',
        ),
    ]
