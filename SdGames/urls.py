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
from appPrincipal.views import home, menu

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home),
    path('menu/', menu),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) #Esto se supone que permite subir imagenes aun no puedo probar si realmente funciona

# esto es para editar titulos en el panel de administracion
admin.site.index_title="SD Games"
admin.site.site_header="Administración SD Games"
admin.site.site_title="Sitio de administración de SD Games"