# Generated by Django 4.1.1 on 2023-03-18 20:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0021_alter_lostvehicle_chasisnumber_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lostvehicle',
            name='regNumber',
            field=models.CharField(default='N/A', max_length=30),
        ),
    ]
