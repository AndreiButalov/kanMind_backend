# Generated by Django 5.2.3 on 2025-07-02 08:08

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kanMind_app', '0001_initial'),
        ('user_auth_app', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='task',
            old_name='assignee_id',
            new_name='assignees',
        ),
        migrations.RemoveField(
            model_name='task',
            name='reviewer_id',
        ),
        migrations.AddField(
            model_name='task',
            name='reviewer',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='review_tasks', to='user_auth_app.userprofile'),
        ),
        migrations.AlterField(
            model_name='board',
            name='members',
            field=models.ManyToManyField(blank=True, related_name='boards', to='user_auth_app.userprofile'),
        ),
        migrations.AlterField(
            model_name='comment',
            name='author',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='user_auth_app.userprofile'),
        ),
    ]
