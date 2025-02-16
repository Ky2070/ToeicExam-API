# Generated by Django 5.1.2 on 2025-02-16 13:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0021_blog_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='blog',
            name='status',
            field=models.CharField(choices=[('ACTIVE', 'Active'), ('INACTIVE', 'Inactive'), ('DELETED', 'Deleted')], default='INACTIVE', max_length=30),
        ),
    ]
