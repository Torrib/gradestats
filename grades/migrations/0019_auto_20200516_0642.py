# Generated by Django 3.0 on 2020-05-16 06:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("grades", "0018_auto_20200515_1746"),
    ]

    operations = [
        migrations.AlterField(
            model_name="department",
            name="department_id",
            field=models.PositiveIntegerField(verbose_name="InstituttsID"),
        ),
    ]