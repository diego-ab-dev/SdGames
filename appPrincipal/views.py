from django.shortcuts import render, get_object_or_404, redirect
from .models import Producto ,ItemCarritoProducto, Usuario, Carrito
from appPrincipal import forms
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.http import JsonResponse, Http404
from django.db.models import Avg
from django.contrib.auth.hashers import make_password, check_password
# Create your views here.

def obtener_ciudades(request):
    region = request.GET.get('region')
    ciudades = regiones_ciudades.get(region, [])
    return JsonResponse({'ciudades': ciudades})


def productos_menu(request):
    query=request.GET.get('buscar')
    if query:
        productos=Producto.objects.filter(nombre__icontains=query)
        return render(request, 'resultado_busqueda.html', {'productos': productos, 'query':query})
    else:
        productos = Producto.objects.all() 
        return render(request, 'productosmenu.html', {'productos': productos})
    
def productos_por_categoria(request, categoria):
    # Obtener todos los productos de la categoría
    productos = Producto.objects.filter(categoria=categoria)
    
    # Filtrar por género
    genero = request.GET.get('genero')
    if genero:
        productos = productos.filter(genero=genero)
    
    # Filtrar por rango de precio
    precio_min = request.GET.get('precio_min')
    precio_max = request.GET.get('precio_max')
    if precio_min and precio_max:
        productos = productos.filter(precio__gte=precio_min, precio__lte=precio_max)
    
    context = {
        'categoria': dict(Producto.CATEGORIAS).get(categoria, categoria),
        'productos': productos,
        'generos': Producto.GENEROS,  # Para mostrar los géneros en la barra lateral
    }
    return render(request, 'productos_por_categoria.html', context)


def home(request):
    usuario_id = request.session.get('usuario_id')
    usuario = None
    if usuario_id:
        try:
            usuario = Usuario.objects.get(id=usuario_id)
        except Usuario.DoesNotExist:
            pass
    return render(request, 'home.html', {'usuario': usuario})


def login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        contraseña = request.POST.get('contraseña')
        
        try:
            usuario = Usuario.objects.get(email=email)
            if check_password(contraseña, usuario.contraseña):  
                request.session['usuario_id'] = usuario.id
                messages.success(request, f"Bienvenido/a {usuario.nombre}")
                return redirect('home')
            else:
                messages.error(request, "Credenciales incorrectas. Intente nuevamente.")
        except Usuario.DoesNotExist:
            messages.error(request, "Credenciales incorrectas. Intente nuevamente.")
    
    return render(request, 'login.html')

def logout(request):
    request.session.flush()  
    messages.success(request, "Sesión cerrada exitosamente.")
    return redirect('login')
    
def register(request):
    form = forms.Usuario()
    if request.method == 'POST':
        print(request.POST)
        form = forms.Usuario(request.POST)
        region_seleccionada = request.POST.get('region')
        ciudades = regiones_ciudades.get(region_seleccionada, [])
        form.fields['ciudad'].choices = [(ciudad, ciudad) for ciudad in ciudades]

        if form.is_valid():
            registro = Usuario(
                nombre=form.cleaned_data['nombre'],
                telefono=form.cleaned_data['telefono'],
                email=form.cleaned_data['email'],
                contraseña=make_password(form.cleaned_data['contraseña']),
                direccion=form.cleaned_data['direccion'],
                ciudad=form.cleaned_data['ciudad'],
                region=form.cleaned_data['region'],
            )
            registro.save()
            messages.success(request, "Usuario registrado correctamente.")
            return redirect('home')
        else:
            print(form.errors)
            messages.error(request, "Hubo un error en el formulario.")
    data = {'form': form, 'regiones_ciudades': regiones_ciudades}
    return render(request, 'register.html', data)


def perfil(request):
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        messages.error(request, "Debes iniciar sesión para acceder al perfil.")
        return redirect('login')
    
    usuario = get_object_or_404(Usuario, id=usuario_id)
    return render(request, 'perfil_usuario.html', {'usuario': usuario})


def cambiar_contraseña(request):
    if request.method == 'POST':
        nueva_contraseña = request.POST.get('nueva_contraseña')
        confirmar_contraseña = request.POST.get('confirmar_contraseña')
        
        if nueva_contraseña != confirmar_contraseña:
            messages.error(request, "Las contraseñas no coinciden. Inténtelo nuevamente.")
        else:
            usuario_id = request.session.get('usuario_id')
            if usuario_id:
                try:
                    usuario = Usuario.objects.get(id=usuario_id)
                    usuario.contraseña = make_password(nueva_contraseña)  
                    usuario.save()
                    messages.success(request, "Contraseña actualizada exitosamente.")
                    return redirect('perfil')
                except Usuario.DoesNotExist:
                    messages.error(request, "Usuario no encontrado.")
            else:
                messages.error(request, "Debes iniciar sesión para cambiar tu contraseña.")
    return render(request, 'cambiar_contrausu.html')

@csrf_exempt
def editar_perfil(request):
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        messages.error(request, "Debes iniciar sesión para acceder a la edición de perfil.")
        return redirect('login')

    usuario = get_object_or_404(Usuario, id=usuario_id)

    if request.method == 'POST':
        telefono = request.POST.get('telefono')
        direccion = request.POST.get('direccion')
        region = request.POST.get('region')
        ciudad = request.POST.get('ciudad')

        if region and ciudad not in regiones_ciudades.get(region, []):
            return JsonResponse({'error': 'La ciudad no coincide con la región seleccionada.'}, status=400)

        usuario.telefono = telefono or usuario.telefono
        usuario.direccion = direccion or usuario.direccion
        usuario.region = region or usuario.region
        usuario.ciudad = ciudad or usuario.ciudad
        usuario.save()

        return JsonResponse({'success': 'Perfil actualizado correctamente.'})

    ciudades = regiones_ciudades.get(usuario.region, [])
    context = {
        'usuario': usuario,
        'regiones': regiones_ciudades.keys(),
        'ciudades': ciudades,
    }
    return render(request, 'editar_datos.html', context)

def producto_detalle(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    rango_cantidad = range(1, producto.stock + 1)

    promedio_puntuacion = producto.opiniones.aggregate(Avg('puntuacion'))['puntuacion__avg']
    promedio_puntuacion = round(promedio_puntuacion, 1) if promedio_puntuacion else 0

    opiniones = producto.opiniones.all()
    opiniones_list = [
        {
            "usuario": opinion.usuario.nombre,
            "comentario": opinion.comentario,
            "fecha": opinion.fecha_creacion,
            "estrellas_llenas": range(opinion.puntuacion),  
            "estrellas_vacias": range(5 - opinion.puntuacion),  
        }
        for opinion in opiniones
    ]

    return render(
        request,
        'producto_detalle.html',
        {
            'producto': producto,
            'rango_cantidad': rango_cantidad,
            'promedio_puntuacion': promedio_puntuacion,
            'opiniones_list': opiniones_list,  
        },
    )

def usuario_compro_producto(usuario, producto):
    return ItemCarritoProducto.objects.filter(
        carrito__venta__isnull=False,  
        carrito__usuario=usuario,
        producto=producto
    ).exists()


def vista_carrusel(request):
    productos = Producto.objects.all()
    cod6 = Producto.objects.filter(nombre="Call of Duty: Black Ops 6").first() 
    fc25 = Producto.objects.filter(nombre="Fc 25").first()
    silent = Producto.objects.filter(nombre="Silent Hill 2").first()    
    return render(request, 'productosmenu.html', {'productos': productos, 'cod6': cod6, 'fc25': fc25, 'silent':silent})

def agregar_al_carrito(request, producto_id):
    usuario_id = request.session.get('usuario_id')
    
    if not usuario_id:
        return redirect('login') 

    try:
        usuario = Usuario.objects.get(id=usuario_id)
    except Usuario.DoesNotExist:
        raise Http404("Usuario no encontrado") 
    carrito, created = Carrito.objects.get_or_create(usuario=usuario, estado='E')

    try:
        producto = Producto.objects.get(id=producto_id)
    except Producto.DoesNotExist:
        raise Http404("Producto no encontrado")  
    item_carrito, item_created = ItemCarritoProducto.objects.get_or_create(
        carrito=carrito, producto=producto
    )

    if not item_created:
        item_carrito.cantidad += 1
        item_carrito.save()

    else:
        item_carrito.cantidad = 1
        item_carrito.save()

    return redirect('ver_carrito')  

def eliminar_del_carrito(request, item_id):
    item = get_object_or_404(ItemCarritoProducto, id=item_id)
    item.delete()
    return redirect('carrito')

def actualizar_cantidad_carrito(request):
    if request.method == 'POST':
        item_id = request.POST.get('item_id')
        nueva_cantidad = int(request.POST.get('cantidad'))
        item = get_object_or_404(ItemCarritoProducto, id=item_id)
        if nueva_cantidad > 0:
            item.cantidad = nueva_cantidad
            item.save()
        else:
            item.delete()
        return JsonResponse({'success': True, 'total': item.carrito.total_carrito()})
    return JsonResponse({'success': False})

def ver_carrito(request):
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return redirect('login')

    try:
        usuario = Usuario.objects.get(id=usuario_id)
    except Usuario.DoesNotExist:
        raise Http404("Usuario no encontrado")

    carrito, created = Carrito.objects.get_or_create(usuario=usuario, estado='E')

    return render(request, 'carrito.html', {
        'carrito': carrito,
        'productos': carrito.items.all(), 
        'total': carrito.total_carrito()
    })

def carrito(request):
    return render(request, 'carrito.html')

def lista_favoritos(request):
    return render(request, 'favorite.html')



# Diccionario de regiones y ciudades
regiones_ciudades = {
    'ARICA Y PARINACOTA': ['Arica', 'Putre'],
    'TARAPACA': ['Iquique', 'Alto Hospicio'],
    'ANTOFAGASTA': ['Antofagasta', 'Calama', 'Tocopilla'],
    'ATACAMA': ['Copiapó', 'Vallenar', 'Chañaral'],
    'COQUIMBO': ['La Serena', 'Coquimbo', 'Ovalle'],
    'VALPARAISO': ['Valparaíso', 'Viña del Mar', 'Quillota', 'San Antonio'],
    'METROPOLITANA': ['Santiago', 'Puente Alto', 'Maipú', 'La Florida'],
    'OHIGGINS': ['Rancagua', 'San Fernando', 'Pichilemu'],
    'MAULE': ['Talca', 'Curicó', 'Linares'],
    'ÑUBLE': ['Chillán', 'San Carlos'],
    'BIOBIO': ['Concepción', 'Los Ángeles', 'Coronel'],
    'ARAUCANIA': ['Temuco', 'Villarrica', 'Angol'],
    'LOS RIOS': ['Valdivia', 'La Unión'],
    'LOS LAGOS': ['Puerto Montt', 'Osorno', 'Castro'],
    'AYSEN': ['Coyhaique', 'Puerto Aysén'],
    'MAGALLANES': ['Punta Arenas', 'Puerto Natales'],
}

def metodo_pago(request):
    if request.method == 'POST':
        # Obtener los datos enviados en el POST
        region = request.POST.get('region')
        ciudad = request.POST.get('ciudad')
        tipo_entrega = request.POST.get('tipo_entrega')
        metodo_pago = request.POST.get('metodo_pago')
        numero_tarjeta = request.POST.get('numero_tarjeta')
        fecha_vencimiento = request.POST.get('fecha_vencimiento')
        codigo_seguridad = request.POST.get('codigo_seguridad')
        nombre_titular = request.POST.get('nombre_titular')

        # Validar los datos o hacer el procesamiento necesario
        if not region or not ciudad or not metodo_pago:
            messages.error(request, "Por favor complete todos los campos requeridos.")
        else:
            messages.success(request, "Pago procesado correctamente.")
            # Realiza el procesamiento del pago aquí

    # Pasar las regiones y ciudades a la plantilla
    return render(request, 'metodo_pago.html', {'regiones_ciudades': regiones_ciudades})

regiones_ciudades = {
    'ARICA Y PARINACOTA': ['Arica', 'Putre'],
    'TARAPACA': ['Iquique', 'Alto Hospicio'],
    'ANTOFAGASTA': ['Antofagasta', 'Calama', 'Tocopilla'],
    'ATACAMA': ['Copiapó', 'Vallenar', 'Chañaral'],
    'COQUIMBO': ['La Serena', 'Coquimbo', 'Ovalle'],
    'VALPARAISO': ['Valparaíso', 'Viña del Mar', 'Quillota', 'San Antonio'],
    'METROPOLITANA': ['Santiago', 'Puente Alto', 'Maipú', 'La Florida'],
    'OHIGGINS': ['Rancagua', 'San Fernando', 'Pichilemu'],
    'MAULE': ['Talca', 'Curicó', 'Linares'],
    'ÑUBLE': ['Chillán', 'San Carlos'],
    'BIOBIO': ['Concepción', 'Los Ángeles', 'Coronel'],
    'ARAUCANIA': ['Temuco', 'Villarrica', 'Angol'],
    'LOS RIOS': ['Valdivia', 'La Unión'],
    'LOS LAGOS': ['Puerto Montt', 'Osorno', 'Castro'],
    'AYSEN': ['Coyhaique', 'Puerto Aysén'],
    'MAGALLANES': ['Punta Arenas', 'Puerto Natales'],
}