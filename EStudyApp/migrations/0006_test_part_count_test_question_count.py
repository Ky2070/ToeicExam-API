# Generated by Django 5.1.2 on 2024-11-22 11:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('EStudyApp', '0005_alter_question_question_text'),
    ]

    operations = [
        migrations.AddField(
            model_name='test',
            name='part_count',
            field=models.IntegerField(default=7),
        ),
        migrations.AddField(
            model_name='test',
            name='question_count',
            field=models.IntegerField(default=200),
        ),
    ]
