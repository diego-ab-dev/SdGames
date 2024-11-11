from django.db import models

# Todas las tablas se ven en mi azure SQL DataBase, agregue "imagen" en la clase producto
# para que permita subir imagenes al momento de crear un nuevo producto desde el panel de admin

class Usuario(models.Model):
    nombre = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    contraseña = models.CharField(max_length=100)
    telefono = models.CharField(max_length=20, verbose_name="Teléfono")
    direccion = models.CharField(max_length=120, verbose_name="Dirección")

    def __str__(self):
        return self.nombre

class Producto(models.Model):
    codigo_de_barra = models.CharField(max_length=20, unique=True, verbose_name="Código de Barra") 
    nombre = models.CharField(max_length=100)
    precio = models.PositiveIntegerField(default=0)  
    stock = models.PositiveIntegerField(default=0)  
    descripcion = models.TextField(blank=True, null=True, default='', verbose_name="Descripción")
    imagen = models.ImageField(upload_to='productos/')

    def agregar_producto(self):
        pass 

    def editar_producto(self):
        pass

    def eliminar_producto(self):
        pass

class Carrito(models.Model):
    TIPO_CHOICES = [
        ('E', 'En Proceso'),
        ('C', 'Completado'),
    ]
    tipo = models.CharField(max_length=1, choices=TIPO_CHOICES, null=True, blank=True, default='E')
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='carritos')

    def genera_venta(self):
        pass

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
        pass

    def genera_boleta(self):
        pass

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


