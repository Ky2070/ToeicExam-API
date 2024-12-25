# Generated by Django 5.1.2 on 2024-12-23 17:43

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0012_blog_created_at_blog_updated_at'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name='blog',
            name='author',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='blog_user', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='commentblog',
            name='blog',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='commentblog_blog', to='course.blog'),
        ),
        migrations.AlterField(
            model_name='commentblog',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='commentblog_user', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='course',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='course_user', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='lesson',
            name='course',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='lesson_course', to='course.course'),
        ),
        migrations.AlterField(
            model_name='reviewlesson',
            name='lesson',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='reviewlesson_lesson', to='course.lesson'),
        ),
        migrations.AlterField(
            model_name='reviewlesson',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='reviewlesson_user', to=settings.AUTH_USER_MODEL),
        ),
    ]
