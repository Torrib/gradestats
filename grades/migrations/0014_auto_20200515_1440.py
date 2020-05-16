# Generated by Django 3.0 on 2020-05-15 14:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("grades", "0013_merge_20200515_1353"),
    ]

    operations = [
        migrations.AlterField(
            model_name="course",
            name="code",
            field=models.CharField(max_length=15, unique=True, verbose_name="Code"),
        ),
        migrations.AlterField(
            model_name="course",
            name="study_level",
            field=models.SmallIntegerField(default=0),
        ),
    ]
