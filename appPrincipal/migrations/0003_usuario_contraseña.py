# Generated by Django 5.0.9 on 2024-11-13 17:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appPrincipal', '0002_remove_usuario_is_active'),
    ]

    operations = [
        migrations.AddField(
            model_name='usuario',
            name='contraseña',
            field=models.CharField(default='', max_length=100),
        ),
    ]
