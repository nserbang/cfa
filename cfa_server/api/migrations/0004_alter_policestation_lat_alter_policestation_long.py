# Generated by Django 4.1 on 2023-03-13 11:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_alter_cuser_role_alter_policestation_lat_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='policestation',
            name='lat',
            field=models.DecimalField(decimal_places=10, default=0.0, max_digits=20),
        ),
        migrations.AlterField(
            model_name='policestation',
            name='long',
            field=models.DecimalField(decimal_places=10, default=0.0, max_digits=20),
        ),
    ]
