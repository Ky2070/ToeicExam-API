# Generated by Django 5.1.2 on 2024-11-06 06:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('EStudyApp', '0002_question_part_question_test_questionset_part_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='question',
            name='difficulty_level',
            field=models.CharField(blank=True, choices=[('BASIC', 'Basic'), ('MEDIUM', 'Medium'), ('DIFFICULTY', 'Difficulty'), ('VERY_DIFFICULTY', 'Very Difficulty')], default='', max_length=30, null=True),
        ),
    ]