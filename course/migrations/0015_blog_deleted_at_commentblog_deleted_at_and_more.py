# Generated by Django 5.1.2 on 2024-12-25 17:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0014_alter_reviewlesson_created_at_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='blog',
            name='deleted_at',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='commentblog',
            name='deleted_at',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='course',
            name='deleted_at',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='lesson',
            name='deleted_at',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='reviewlesson',
            name='deleted_at',
            field=models.DateTimeField(null=True),
        ),
    ]