# Generated by Django 5.1.2 on 2024-12-04 06:20

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('EStudyApp', '0008_test_part_count_test_question_count'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='State',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=125, null=True)),
                ('info', models.JSONField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=125, null=True)),
                ('description', models.CharField(blank=True, max_length=125, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='HistoryTraining',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_time', models.DateTimeField(blank=True, null=True)),
                ('end_time', models.DateTimeField(blank=True, null=True)),
                ('correct_answers', models.IntegerField(blank=True, null=True)),
                ('wrong_answers', models.IntegerField(blank=True, null=True)),
                ('unanswer_questions', models.IntegerField(blank=True, null=True)),
                ('percentage_score', models.DecimalField(blank=True, decimal_places=1, max_digits=4, null=True)),
                ('complete', models.BooleanField(default=False)),
                ('test_result', models.JSONField(blank=True, null=True)),
                ('part', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='training_part', to='EStudyApp.part')),
                ('test', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='training_test', to='EStudyApp.test')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='training_user', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='test',
            name='tag',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='test_tag', to='EStudyApp.tag'),
        ),
        migrations.CreateModel(
            name='TestComment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField()),
                ('publish_date', models.DateTimeField(auto_now_add=True)),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='replies', to='EStudyApp.testcomment')),
                ('test', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='testcomment_test', to='EStudyApp.test')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='testcomment_user', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
