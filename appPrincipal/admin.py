from django.contrib import admin
from .models import Usuario, Producto, Venta, Reclamo

# Register your models here.

class ProductoAdmin(admin.ModelAdmin):
    list_display=("codigo_de_barra", "nombre", "precio", "stock", "imagen_display")
    search_fields=("nombre", "codigo_de_barra")
    
    def imagen_display(self, obj):
        if obj.imagen:
            return obj.imagen.url
        return 'Sin imagen'
    imagen_display.short_description = 'Imagen'

class UsuarioAdmin(admin.ModelAdmin):
    list_display=("nombre", "email", "telefono", "direccion")
    search_fields=("nombre", "email", "telefono")

class VentaAdmin(admin.ModelAdmin):
    list_display=("total", "estado", "fecha")
    list_filter=("estado", "fecha",)
    date_hierarchy="fecha"

class ReclamoAdmin(admin.ModelAdmin):
    list_display=("usuario", "estado", "descripcion")
    list_filter=("estado",)

admin.site.register(Usuario, UsuarioAdmin)
admin.site.register(Producto, ProductoAdmin)
admin.site.register(Venta, VentaAdmin)
admin.site.register(Reclamo, ReclamoAdmin)

