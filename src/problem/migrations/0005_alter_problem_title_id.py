# Generated by Django 3.2.9 on 2021-12-10 21:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('problem', '0004_problem_title_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='problem',
            name='title_id',
            field=models.CharField(max_length=32),
        ),
    ]