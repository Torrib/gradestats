# Generated by Django 3.0 on 2020-05-15 17:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("grades", "0015_auto_20200515_1719"),
    ]

    operations = [
        migrations.CreateModel(
            name="Faculty",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("acronym", models.CharField(max_length=32, verbose_name="Akronym")),
                (
                    "norwegian_name",
                    models.CharField(max_length=256, verbose_name="Norsk navn"),
                ),
                (
                    "english_name",
                    models.CharField(max_length=256, verbose_name="Engelsk navn"),
                ),
                (
                    "organization_unit_id",
                    models.IntegerField(
                        help_text="NTNU ID", unique=True, verbose_name="OuID"
                    ),
                ),
                (
                    "nsd_code",
                    models.CharField(max_length=32, verbose_name="Code fra NSD"),
                ),
                (
                    "faculty_id",
                    models.PositiveIntegerField(
                        unique=True, verbose_name="FakultetsID"
                    ),
                ),
            ],
            options={
                "verbose_name": "Fakultet",
                "verbose_name_plural": "Fakulteter",
                "ordering": ("norwegian_name",),
            },
        ),
        migrations.CreateModel(
            name="Department",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("acronym", models.CharField(max_length=32, verbose_name="Akronym")),
                (
                    "norwegian_name",
                    models.CharField(max_length=256, verbose_name="Norsk navn"),
                ),
                (
                    "english_name",
                    models.CharField(max_length=256, verbose_name="Engelsk navn"),
                ),
                (
                    "organization_unit_id",
                    models.IntegerField(
                        help_text="NTNU ID", unique=True, verbose_name="OuID"
                    ),
                ),
                (
                    "nsd_code",
                    models.CharField(max_length=32, verbose_name="Code fra NSD"),
                ),
                (
                    "department_id",
                    models.PositiveIntegerField(
                        unique=True, verbose_name="InstituttsID"
                    ),
                ),
                (
                    "faculty",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="departments",
                        to="grades.Faculty",
                    ),
                ),
            ],
            options={
                "verbose_name": "Institutt",
                "verbose_name_plural": "Institutter",
                "ordering": ("norwegian_name",),
            },
        ),
    ]