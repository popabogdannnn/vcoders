# Generated by Django 3.2.9 on 2021-12-14 19:40

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('problem', '0005_alter_problem_title_id'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='problem',
            name='statement',
        ),
        migrations.AddField(
            model_name='problem',
            name='accepted',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='problem',
            name='author',
            field=models.CharField(default='-', max_length=32),
        ),
        migrations.AddField(
            model_name='problem',
            name='posted_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
    ]