# Generated by Django 3.2.6 on 2021-10-05 15:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('eval', '0002_refactor_percent_to_score'),
    ]

    operations = [
        migrations.AlterField(
            model_name='projectfunctionality',
            name='description',
            field=models.CharField(max_length=1024),
        ),
    ]