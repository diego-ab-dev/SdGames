from django.contrib import admin
from .models import Usuario, Producto, Venta, Reclamo

# Register your models here.

class ProductoAdmin(admin.ModelAdmin):
    list_display = ('codigo_de_barra', 'nombre', 'precio', 'stock', 'imagen_display')
    search_fields = ('nombre', 'codigo_de_barra')
    
    def imagen_display(self, obj):
        if obj.imagen:
            return obj.imagen.url
        return 'Sin imagen'
    imagen_display.short_description = 'Imagen'

admin.site.register(Usuario)
admin.site.register(Producto)
admin.site.register(Venta)
admin.site.register(Reclamo)

