# Generated by Django 4.0.1 on 2022-03-22 21:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('problem', '0007_auto_20211216_1538'),
    ]

    operations = [
        migrations.AddField(
            model_name='problem',
            name='can_submit',
            field=models.BooleanField(default=False),
        ),
    ]