# Generated by Django 3.2.9 on 2021-12-13 23:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('submissions', '0006_submission_compiler_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='submission',
            name='verdict',
            field=models.CharField(default='-', max_length=32),
        ),
    ]
