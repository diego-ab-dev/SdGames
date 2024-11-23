# Generated by Django 5.0.9 on 2024-11-23 16:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appPrincipal', '0004_alter_usuario_ciudad'),
    ]

    operations = [
        migrations.AlterField(
            model_name='producto',
            name='categoria',
            field=models.CharField(choices=[('VIDEOJUEGOS', [('Videojuegos PS3', 'PlayStation 3'), ('Videojuegos PS4', 'PlayStation 4'), ('Videojuegos PS5', 'PlayStation 5'), ('Videojuegos XBOX 360', 'Xbox 360'), ('Videojuegos XBOX ONE', 'Xbox One'), ('Videojuegos XBOX SERIES', 'Xbox Series'), ('Videojuegos Nintendo 3DS', 'Nintendo 3DS'), ('Videojuegos WII', 'Nintendo Wii'), ('Videojuegos WII U', 'Nintendo Wii U'), ('Videojuegos Nintendo SWITCH', 'Nintendo Switch'), ('Videojuegos para PC', 'PC')]), ('CONSOLAS', [('Ps4 Consola', 'Consola PlayStation 4'), ('Ps5 Consola', 'Consola PlayStation 5'), ('Xbox One Consolas', 'Consola Xbox One'), ('Xbox Series Consolas', 'Consola Xbox Series'), ('Wii U Consola', 'Consola Wii U'), ('Switch Consola', 'Consola Switch')]), ('ACCESORIOS', [('Accesorios Psp', 'PSP'), ('Accesorios Ps Vita', 'PlayStation Vita'), ('Accesorios PS1', 'PlayStation 1'), ('Accesorios PS2', 'PlayStation 2'), ('Accesorios PS3', 'PlayStation 3'), ('Accesorios PS4', 'PlayStation 4'), ('Accesorios PS5', 'PlayStation 5'), ('Accesorios XBOX 360', 'Xbox 360'), ('Accesorios XBOX ONE', 'Xbox One'), ('Accesorios XBOX SERIES', 'Xbox Series'), ('Accesorios N3DS', 'Nintendo 3DS'), ('Accesorios WII U', 'Wii U'), ('Accesorios Nintendo SWITCH', 'Switch')]), ('FIGURAS', [('Figuras Funko', 'Funko Pop'), ('Figuras Amiibo', 'Amiibo')])], max_length=40, verbose_name='Categoría'),
        ),
    ]
