# Generated by Django 4.1 on 2023-03-13 11:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_alter_policestation_lat_alter_policestation_long'),
    ]

    operations = [
        migrations.AlterField(
            model_name='policestation',
            name='lat',
            field=models.DecimalField(decimal_places=6, default=0.0, max_digits=9),
        ),
        migrations.AlterField(
            model_name='policestation',
            name='long',
            field=models.DecimalField(decimal_places=6, default=0.0, max_digits=9),
        ),
    ]
