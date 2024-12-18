# Generated by Django 5.1.2 on 2024-12-18 08:59

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('EStudyApp', '0022_remove_commentblog_blog_remove_commentblog_parent_and_more'),
        ('course', '0008_lesson_video_alter_lesson_content_alter_lesson_title'),
    ]

    operations = [
        migrations.AddField(
            model_name='blog',
            name='questions_set',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='blog_questions_set', to='EStudyApp.questionset'),
        ),
    ]