# Generated by Django 5.1.2 on 2024-12-22 18:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('EStudyApp', '0026_alter_part_part_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='questionset',
            name='from_ques',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
