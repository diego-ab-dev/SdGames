from django.shortcuts import render, get_object_or_404, redirect
from .models import Producto
from appPrincipal import forms
from .models import Usuario
from django.contrib import messages
from .models import Usuario
# Create your views here.


def productos_menu(request):
    query=request.GET.get('buscar')
    if query:
        productos=Producto.objects.filter(nombre__icontains=query)
        return render(request, 'resultado_busqueda.html', {'productos': productos, 'query':query})
    else:
        productos = Producto.objects.all() 
        return render(request, 'productosmenu.html', {'productos': productos})
    
def productos_por_categoria(request, categoria):
    productos = Producto.objects.filter(categoria=categoria)
    context = {
        'categoria': dict(Producto.CATEGORIAS).get(categoria, categoria),
        'productos': productos,
    }
    return render(request, 'productos_por_categoria.html', context)


def home(request):
    return render(request, 'home.html')

def login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        contraseña = request.POST.get('contraseña')
        
        try:
            usuario = Usuario.objects.get(email=email, contraseña=contraseña)
            request.session['usuario_id'] = usuario.id 
            messages.success(request, f"Bienvenido/a {usuario.nombre}")
            return redirect('home')  
        except Usuario.DoesNotExist:
            messages.error(request, "Credenciales incorrectas. Intente nuevamente.")
            return redirect('login')  
    
    return render(request, 'login.html')

def logout(request):
    request.session.flush()  
    messages.success(request, "Sesión cerrada exitosamente.")
    return redirect('login')
    
def register(request):
    form=forms.Usuario()
    if request.method == 'POST':
        form=forms.Usuario(request.POST)
        if form.is_valid():
            registro = Usuario(
                nombre=form.cleaned_data['nombre'],
                telefono=form.cleaned_data['telefono'],
                email = form.cleaned_data['email'],
                contraseña = form.cleaned_data['contraseña'],
                direccion =  form.cleaned_data['direccion'],
            )
            registro.save()  
        else:
            print(form.errors)  
    data={'form':form}
    return render(request, 'register.html', data)


def producto_detalle(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    return render(request, 'producto_detalle.html', {'producto': producto})

def vista_carrusel(request):
    productos = Producto.objects.all()
    cod6 = Producto.objects.filter(nombre="Call of Duty: Black Ops 6").first() 
    fc25 = Producto.objects.filter(nombre="Fc 25").first()
    silent = Producto.objects.filter(nombre="Silent Hill 2").first()    
    return render(request, 'productosmenu.html', {'productos': productos, 'cod6': cod6, 'fc25': fc25, 'silent':silent})

def carrito(request):
    return render(request, 'carrito.html')

