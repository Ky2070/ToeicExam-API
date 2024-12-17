# Generated by Django 5.1.2 on 2024-12-17 15:13

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0004_alter_course_title'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='banner',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='course',
            name='info',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(blank=True, max_length=255, null=True), blank=True, null=True, size=None),
        ),
        migrations.AddField(
            model_name='course',
            name='target',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(blank=True, max_length=255, null=True), blank=True, null=True, size=None),
        ),
    ]