# Generated by Django 4.1 on 2023-03-13 17:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0008_rename_d1_policestation_distance'),
    ]

    operations = [
        migrations.RenameField(
            model_name='policestationcontact',
            old_name='cid',
            new_name='ps_cid',
        ),
    ]
