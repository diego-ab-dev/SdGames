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
from appPrincipal.views import home, login, register, productos_menu, producto_detalle, carrito, vista_carrusel, logout, productos_por_categoria

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name="home"),
    path('home/', home, name="home"),
    path('productos_menu/', productos_menu, name='productos_menu_vista'),
    path('menu/', vista_carrusel, name='productos_menu'),
    path('carrito/', carrito),
    path('producto/<int:producto_id>/', producto_detalle, name='producto_detalle'),
    path('productos/<str:categoria>/', productos_por_categoria, name='productos_por_categoria'),
    path('login/', login),
    path('register/', register),
    path('carrito/', carrito),
    path('logout/', logout, name='logout'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) #Esto se supone que permite subir imagenes aun no puedo probar si realmente funciona

# esto es para editar titulos en el panel de administracion
admin.site.index_title="SD Games"
admin.site.site_header="Administración SD Games"
admin.site.site_title="Sitio de administración de SD Games"