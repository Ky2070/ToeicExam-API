# Generated by Django 5.1.2 on 2025-02-27 11:42

import ckeditor.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('question_bank', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='questionsetbank',
            name='page',
            field=ckeditor.fields.RichTextField(blank=True, null=True),
        ),
    ]
