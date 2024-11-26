from django.contrib import admin
from .models import Usuario, Producto, Venta, Reclamo, Opinion

# Edite admin.py para que se reflejen los datos de las tablas en el panel de administracion que ofrece django
# Las tablas "ItemCarritoProducto" y "Carrito" no aparecen en el panel de admin ya que no tiene mucho sentido que las pueda ver

class ProductoAdmin(admin.ModelAdmin):
    list_display = ("codigo_de_barra", "nombre", "precio", "stock", "imagen_display", "categoria", "genero")
    search_fields = ("nombre", "codigo_de_barra")
    list_editable = ("stock", "categoria", "genero")
    list_filter=("categoria", "genero")
    list_per_page = 20

    def imagen_display(self, obj):
        if obj.imagen_principal:
            return obj.imagen_principal.url
        return 'Sin imagen'
    imagen_display.allow_tags = True
    imagen_display.short_description = 'Imagen Principal'

class UsuarioAdmin(admin.ModelAdmin):
    list_display = ("nombre", "email", "rut", "telefono", "direccion", "ciudad", "region")
    search_fields = ("nombre", "email", "telefono",)
    list_per_page = 20
    inlines = []

    def ventas_asociadas(self, obj):
        ventas = obj.ventas.all()
        return ", ".join([f"#{venta.id} - ${venta.total}" for venta in ventas]) if ventas else "Sin ventas"
    ventas_asociadas.short_description = "Ventas Asociadas"

    readonly_fields = ["ventas_asociadas"]


class VentaAdmin(admin.ModelAdmin):
    list_display = ("usuario", "productos_comprados", "total", "estado", "fecha", "metodo_envio", "direccion_envio")
    list_filter = ("estado", "fecha",)
    list_editable = ("estado",)
    date_hierarchy = "fecha"
    list_per_page = 20

    def productos_comprados(self, obj):
        return ", ".join([f"{item.producto.nombre} (x{item.cantidad})" for item in obj.productos.all()])
    productos_comprados.short_description = "Productos Comprados"


class ReclamoAdmin(admin.ModelAdmin):
    list_display=("usuario", "estado", "descripcion")
    list_filter=("estado",)
    list_per_page=20

admin.site.register(Usuario, UsuarioAdmin)
admin.site.register(Producto, ProductoAdmin)
admin.site.register(Venta, VentaAdmin)
admin.site.register(Reclamo, ReclamoAdmin)
admin.site.register(Opinion)