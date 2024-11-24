from django.db import models

# Todas las tablas se ven en mi azure SQL DataBase, agregue "imagen" en la clase producto
# para que permita subir imagenes al momento de crear un nuevo producto desde el panel de admin

class Usuario(models.Model):
    nombre = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    contraseña = models.CharField(max_length=100, default='')
    rut = models.CharField(max_length=12, default='Rut no especificado' , verbose_name="RUT") 
    telefono = models.CharField(max_length=20, verbose_name="Teléfono")
    direccion = models.CharField(max_length=120, verbose_name="Dirección")
    region = models.CharField(max_length=100, default='Región no especificada')  
    ciudad = models.CharField(max_length=100, default='Ciudad no especificada')
    

    def __str__(self):
        return self.nombre

class Producto(models.Model):
    CATEGORIAS = [
        ('VIDEOJUEGOS', [
            ('Videojuegos PS3', 'PlayStation 3'),
            ('Videojuegos PS4', 'PlayStation 4'),
            ('Videojuegos PS5', 'PlayStation 5'),
            ('Videojuegos XBOX 360', 'Xbox 360'),
            ('Videojuegos XBOX ONE', 'Xbox One'),
            ('Videojuegos XBOX SERIES', 'Xbox Series'),
            ('Videojuegos Nintendo 3DS', 'Nintendo 3DS'),
            ('Videojuegos WII', 'Nintendo Wii'),
            ('Videojuegos WII U', 'Nintendo Wii U'),
            ('Videojuegos Nintendo SWITCH', 'Nintendo Switch'),
            ('Videojuegos para PC', 'PC'),
        ]),
        ('CONSOLAS', [
            ('Ps4 Consolas', 'Consola PlayStation 4'),
            ('Ps5 Consolas', 'Consola PlayStation 5'),
            ('Xbox One Consolas', 'Consola Xbox One'),
            ('Xbox Series Consolas', 'Consola Xbox Series'),
            ('Wii U Consolas', 'Consola Wii U'),
            ('Switch Consolas', 'Consola Switch'),
        ]),
        ('ACCESORIOS', [
            ('Accesorios Psp', 'PSP'),
            ('Accesorios Ps Vita', 'PlayStation Vita'),
            ('Accesorios PS1', 'PlayStation 1'),
            ('Accesorios PS2', 'PlayStation 2'),
            ('Accesorios PS3', 'PlayStation 3'),
            ('Accesorios PS4', 'PlayStation 4'),
            ('Accesorios PS5', 'PlayStation 5'),
            ('Accesorios XBOX 360', 'Xbox 360'),
            ('Accesorios XBOX ONE', 'Xbox One'),
            ('Accesorios XBOX SERIES', 'Xbox Series'),
            ('Accesorios Nintendo 3DS', 'Nintendo 3DS'),
            ('Accesorios WII U', 'Wii U'),
            ('Accesorios Nintendo SWITCH', 'Switch'),
        ]),
        ('FIGURAS', [
            ('Figuras Funko', 'Funko Pop'),
            ('Figuras Amiibo', 'Amiibo'),
        ]),
    ]

    GENEROS = [
        ('ACCION', 'Acción'),
        ('AVENTURA', 'Aventura'),
        ('RPG', 'RPG'),
        ('DEPORTES', 'Deportes'),
        ('CARRERAS', 'Carreras'),
        ('ESTRATEGIA', 'Estrategia'),
        ('SIMULACION', 'Simulación'),
        ('PUZZLE', 'Puzzle'),
        ('TERROR', 'Terror'),
        ('CONSOLAS', 'Consolas'),
        ('FIGURAS', 'Figuras'),
        ('ACCESORIOS', 'Accesorios'),
        ('OTRO', 'Otro'),
    ]
    codigo_de_barra = models.CharField(max_length=20, unique=True, verbose_name="Código de Barra") 
    nombre = models.CharField(max_length=100)
    precio = models.PositiveIntegerField(default=0)  
    stock = models.PositiveIntegerField(default=0)  
    descripcion = models.TextField(blank=True, null=True, default='', verbose_name="Descripción")
    imagen_principal = models.ImageField(upload_to='productos/', verbose_name="Imagen Principal", default='') 
    imagen_2 = models.ImageField(upload_to='productos/', blank=True, null=True, verbose_name="Imagen Opcional 2")
    imagen_3 = models.ImageField(upload_to='productos/', blank=True, null=True, verbose_name="Imagen Opcional 3")
    imagen_4 = models.ImageField(upload_to='productos/', blank=True, null=True, verbose_name="Imagen Opcional 4")
    imagen_5 = models.ImageField(upload_to='productos/', blank=True, null=True, verbose_name="Imagen Opcional 5")
    imagen_6 = models.ImageField(upload_to='productos/', blank=True, null=True, verbose_name="Imagen Opcional 6")
    categoria = models.CharField(max_length=40, choices=CATEGORIAS, verbose_name="Categoría") 
    genero = models.CharField(max_length=20, choices=GENEROS, verbose_name="Género", default='OTRO')


    def imagenes(self):
        return [img for img in [
            self.imagen_principal, self.imagen_2, self.imagen_3, 
            self.imagen_4, self.imagen_5, self.imagen_6] if img]

    def agregar_producto(self):
        pass 

    def editar_producto(self):
        pass

    def eliminar_producto(self):
        pass

    def promedio_puntuacion(self):
        opiniones = self.opiniones.all()
        if not opiniones:
            return 0
        return round(sum(opinion.puntuacion for opinion in opiniones) / len(opiniones), 1)

class Carrito(models.Model):
    TIPO_CHOICES = [
        ('E', 'En Proceso'),
        ('C', 'Completado'),
    ]
    estado = models.CharField(max_length=1, choices=TIPO_CHOICES, null=True, blank=True, default='E')
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='carritos')

    def genera_venta(self):
        pass

    def total_carrito(self):
    # Sumar los totales verificando cantidades y precios válidos
        return sum(
            (item.producto.precio or 0) * max(item.cantidad, 0) for item in self.items.all()
        )

class ItemCarritoProducto(models.Model):
    carrito = models.ForeignKey(Carrito, on_delete=models.CASCADE, related_name='items')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1) 

class Venta(models.Model):
    total = models.PositiveIntegerField(default=0)
    estado = models.CharField(max_length=20, default='Pendiente') 
    fecha = models.DateTimeField(auto_now_add=True)
    carrito = models.OneToOneField(Carrito, on_delete=models.CASCADE)

    def calcular_total(self):
        self.total = sum(item.subtotal() for item in self.carrito.items.all())
        self.save()

    def genera_boleta(self):
        pass

class Opinion(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name="opiniones")
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name="opiniones")
    comentario = models.TextField(verbose_name="Comentario")
    puntuacion = models.PositiveIntegerField(
        verbose_name="Puntuación",
        default=1,
        choices=[(i, str(i)) for i in range(1, 6)] 
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")

    class Meta:
        unique_together = ('usuario', 'producto')  
        verbose_name = "Opinión"
        verbose_name_plural = "Opiniones"

    def __str__(self):
        return f"{self.usuario.nombre} - {self.producto.nombre} ({self.puntuacion} estrellas)"


class Reclamo(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='reclamos')
    estado = models.CharField(max_length=20, default='Abierto')
    descripcion = models.TextField(default='', verbose_name="Descripción")

    def visualizar_reclamo(self):
        pass

    def responder_reclamo(self):
        pass

    def editar_reclamo(self):
        pass