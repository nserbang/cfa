# Generated by Django 4.2.3 on 2023-09-04 15:52

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("api", "0022_lostvehicle_color"),
    ]

    operations = [
        migrations.AddField(
            model_name="policeofficer",
            name="report_on_this",
            field=models.BooleanField(default=False),
        ),
    ]
