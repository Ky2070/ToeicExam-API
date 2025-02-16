# Generated by Django 5.1.2 on 2025-02-16 13:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0020_likeblog'),
    ]

    operations = [
        migrations.AddField(
            model_name='blog',
            name='status',
            field=models.CharField(choices=[('ACTIVE', 'Active'), ('INACTIVE', 'Inactive'), ('DELETED', 'Deleted')], default='ACTIVE', max_length=30),
        ),
    ]
