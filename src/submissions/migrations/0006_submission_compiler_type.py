# Generated by Django 3.2.9 on 2021-12-13 20:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('submissions', '0005_alter_submission_verdict'),
    ]

    operations = [
        migrations.AddField(
            model_name='submission',
            name='compiler_type',
            field=models.CharField(default='c++64', max_length=10),
        ),
    ]
