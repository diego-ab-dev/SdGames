# Generated by Django 5.0.9 on 2024-11-13 17:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('appPrincipal', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='usuario',
            name='is_active',
        ),
    ]