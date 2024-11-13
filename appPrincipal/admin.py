from django.contrib import admin
from .models import Usuario, Producto, Venta, Reclamo

# Edite admin.py para que se reflejen los datos de las tablas en el panel de administracion que ofrece django
# Las tablas "ItemCarritoProducto" y "Carrito" no aparecen en el panel de admin ya que no tiene mucho sentidon que las pueda ver

class ProductoAdmin(admin.ModelAdmin):
    list_display=("codigo_de_barra", "nombre", "precio", "stock", "imagen_display", "categoria")
    search_fields=("nombre", "codigo_de_barra")
    list_editable=("stock",)
    list_per_page=20
    
    def imagen_display(self, obj):
        if obj.imagen:
            return obj.imagen.url
        return 'Sin imagen'
    imagen_display.short_description = 'Imagen'

class UsuarioAdmin(admin.ModelAdmin):
    list_display=("nombre", "email", "telefono", "direccion")
    search_fields=("nombre", "email", "telefono")
    list_per_page=20

class VentaAdmin(admin.ModelAdmin):
    list_display=("total", "estado", "fecha")
    list_filter=("estado", "fecha",)
    date_hierarchy="fecha"
    list_per_page=20

class ReclamoAdmin(admin.ModelAdmin):
    list_display=("usuario", "estado", "descripcion")
    list_filter=("estado",)
    list_per_page=20

admin.site.register(Usuario, UsuarioAdmin)
admin.site.register(Producto, ProductoAdmin)
admin.site.register(Venta, VentaAdmin)
admin.site.register(Reclamo, ReclamoAdmin)

