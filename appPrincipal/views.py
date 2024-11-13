from django.shortcuts import render, get_object_or_404
from .models import Producto

# Create your views here.


def productos_menu(request):
    productos = Producto.objects.all() 
    return render(request, 'productosmenu.html', {'productos': productos})

def home(request):
    return render(request, 'home.html')

def login(request):
    return render(request, 'login.html')

def register(request):
    return render(request, 'register.html')

def producto_detalle(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    return render(request, 'producto_detalle.html', {'producto': producto})

def carrito(request):
    return render(request, 'carrito.html')