# Generated by Django 4.0.1 on 2022-04-10 20:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('problem', '0013_subcontest'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contest',
            name='date',
            field=models.DateField(),
        ),
    ]
