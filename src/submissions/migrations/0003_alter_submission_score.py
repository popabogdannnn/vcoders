# Generated by Django 3.2.9 on 2021-12-13 13:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('submissions', '0002_alter_submission_score'),
    ]

    operations = [
        migrations.AlterField(
            model_name='submission',
            name='score',
            field=models.DecimalField(decimal_places=2, max_digits=5, null=True),
        ),
    ]
