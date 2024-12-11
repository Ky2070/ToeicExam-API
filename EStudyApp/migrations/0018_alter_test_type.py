# Generated by Django 5.1.2 on 2024-12-11 16:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('EStudyApp', '0017_alter_test_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='test',
            name='type',
            field=models.CharField(blank=True, choices=[('ONLINE', 'Online'), ('PRACTICE', 'Practice'), ('ALL', 'All')], max_length=30, null=True),
        ),
    ]
