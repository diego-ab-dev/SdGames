"""
URL configuration for SdGames project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from appPrincipal.views import home, login, register, productos_menu, producto_detalle, carrito, vista_carrusel, logout, productos_por_categoria, perfil, editar_perfil, obtener_ciudades, cambiar_contraseña,  agregar_al_carrito, eliminar_del_carrito, actualizar_cantidad_carrito, ver_carrito, lista_favoritos, agregar_favorito, eliminar_favorito, password_reset_request, ver_compras, lista_opiniones, crear_reclamo, lista_reclamos, seleccionar_envio, seleccionar_pago, compra_exitosa

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name="home"),
    path('home/', home, name="home"),
    path('productos_menu/', productos_menu, name='productos_menu_vista'),
    path('menu/', vista_carrusel, name='productos_menu'),
    path('carrito/', carrito),
    path('producto/<int:producto_id>/', producto_detalle, name='producto_detalle'),
    path('productos/<str:categoria>/', productos_por_categoria, name='productos_por_categoria'),
    path('login/', login, name='login'),
    path('register/', register),
    path('logout/', logout, name='logout'),
    path('perfil/', perfil, name='perfil'),
    path('compras/', ver_compras, name='ver_compras'),
    path('perfil/opiniones/',lista_opiniones, name='lista_opiniones'),
    path('crear_reclamo/<int:compra_id>/', crear_reclamo, name='crear_reclamo'),
    path('reclamos/', lista_reclamos, name='lista_reclamos'),
    path('editar/', editar_perfil, name='editar'),
    path('cambiar/', cambiar_contraseña, name='cambiar'),
    path('carrito/', carrito,  name='carrito'),
    path('ver_carrito/', ver_carrito, name='ver_carrito'),
    path('agregar/<int:producto_id>/', agregar_al_carrito, name='agregar_al_carrito'),
    path('eliminar/<int:item_id>/', eliminar_del_carrito, name='eliminar_del_carrito'),
    path('actualizar-cantidad/', actualizar_cantidad_carrito, name='actualizar_cantidad_carrito'),
    path('favorites/', lista_favoritos, name='lista_favorito'),
    path('agregar_favorito/<int:producto_id>/', agregar_favorito, name='agregar_favorito'),
    path('remove_favorito/<int:item_id>/', eliminar_favorito, name='eliminar_favorito'),
    path('obtener_ciudades/', obtener_ciudades, name='obtener_ciudades'),
    path('password-reset/', password_reset_request, name='password_reset'),
    path('seleccionar-envio/<int:usuario_id>/', seleccionar_envio, name='seleccionar_envio'),
    path('seleccionar-pago/<int:usuario_id>/', seleccionar_pago, name='seleccionar_pago'),
    path('compra-exitosa/<int:usuario_id>/', compra_exitosa, name='compra_exitosa'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) 

# esto es para editar titulos en el panel de administracion
admin.site.index_title="SD Games"
admin.site.site_header="Administración SD Games"
admin.site.site_title="Sitio de administración de SD Games"