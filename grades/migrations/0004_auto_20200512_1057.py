# Generated by Django 3.0 on 2020-05-12 10:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('grades', '0003_auto_20200217_2316'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='grade',
            options={'default_manager_name': 'objects'},
        ),
        migrations.AlterField(
            model_name='grade',
            name='course',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='grades', to='grades.Course'),
        ),
        migrations.AlterField(
            model_name='tag',
            name='courses',
            field=models.ManyToManyField(related_name='tags', to='grades.Course'),
        ),
    ]
