# Generated by Django 5.1.2 on 2024-12-17 13:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0003_alter_course_description'),
    ]

    operations = [
        migrations.AlterField(
            model_name='course',
            name='title',
            field=models.TextField(blank=True, null=True),
        ),
    ]