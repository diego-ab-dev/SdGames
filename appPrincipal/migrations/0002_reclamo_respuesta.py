# Generated by Django 5.0.9 on 2024-11-28 03:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appPrincipal', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='reclamo',
            name='respuesta',
            field=models.TextField(blank=True, null=True, verbose_name='Respuesta del administrador'),
        ),
    ]