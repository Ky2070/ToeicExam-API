# Generated by Django 5.1.2 on 2024-11-22 11:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('EStudyApp', '0006_test_part_count_test_question_count'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='test',
            name='part_count',
        ),
        migrations.RemoveField(
            model_name='test',
            name='question_count',
        ),
    ]