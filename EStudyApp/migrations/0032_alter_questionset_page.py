# Generated by Django 5.1.2 on 2025-02-27 11:45

import ckeditor.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('EStudyApp', '0031_remove_question_update_at_flashcard_created_at_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='questionset',
            name='page',
            field=ckeditor.fields.RichTextField(blank=True, null=True),
        ),
    ]
