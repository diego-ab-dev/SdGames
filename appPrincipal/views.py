from django.shortcuts import render, get_object_or_404, redirect
from .models import Producto ,ItemCarritoProducto, Usuario, Carrito, Venta, ProductoVenta ,Opinion, Favorito, Reclamo
from appPrincipal import forms
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Avg
from django.contrib.auth.hashers import make_password, check_password
from django.conf import settings
import json
from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from django.contrib.messages import get_messages
from django.urls import reverse

# Create your views here.

def password_reset_request(request):
    if request.method == 'POST':
        form = forms.PasswordResetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                usuario = Usuario.objects.get(email=email)
                token = get_random_string(length=32)
                usuario.contraseña = make_password(token)
                usuario.save()
                send_mail(
                    subject="Recuperación de contraseña - SD Games",
                    message=f"Tu nueva contraseña temporal es: {token}",
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[email],
                    fail_silently=False,
                )
                messages.success(request, "Se ha enviado una nueva contraseña a tu correo electrónico.")
                return redirect('login')
            except Usuario.DoesNotExist:
                form.add_error('email', "El correo no está registrado.")
    else:
        form = forms.PasswordResetForm()
    return render(request, 'password_reset.html', {'form': form})

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
        productos_recientes = Producto.objects.order_by('-id')[:10] 
        return render(request, 'productosmenu.html', {
            'productos': productos,
            'productos_recientes': productos_recientes,
        })
    
def productos_por_categoria(request, categoria):
    productos = Producto.objects.filter(categoria=categoria)
    
    genero = request.GET.get('genero')
    if genero:
        productos = productos.filter(genero=genero)
    
    precio_min = request.GET.get('precio_min')
    precio_max = request.GET.get('precio_max')
    if precio_min and precio_max:
        productos = productos.filter(precio__gte=precio_min, precio__lte=precio_max)
    
    orden_precio = request.GET.get('orden_precio')
    if orden_precio == 'asc':
        productos = productos.order_by('precio')
    elif orden_precio == 'desc':
        productos = productos.order_by('-precio')
    
    context = {
        'categoria': dict(Producto.CATEGORIAS).get(categoria, categoria),
        'productos': productos,
        'generos': Producto.GENEROS,
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
    errors = {}  
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        contraseña = request.POST.get('contraseña', '').strip()

        if not email:
            errors['email'] = "Por favor, ingresa tu correo electrónico."
        if not contraseña:
            errors['contraseña'] = "Por favor, ingresa tu contraseña."

        if not errors:
            try:
                usuario = Usuario.objects.get(email=email)
                if check_password(contraseña, usuario.contraseña):  
                    request.session['usuario_id'] = usuario.id
                    return redirect('home')
                else:
                    errors['contraseña'] = "Contraseña incorrecta."
            except Usuario.DoesNotExist:
                errors['email'] = "Correo electrónico no registrado."

    return render(request, 'login.html', {'errors': errors})


def logout(request):
    request.session.flush()  
    return redirect('login')
    
def register(request):
    form = forms.Usuario()
    if request.method == 'POST':
        form = forms.Usuario(request.POST)
        region_seleccionada = request.POST.get('region')
        ciudades = regiones_ciudades.get(region_seleccionada, [])
        form.fields['ciudad'].choices = [(ciudad, ciudad) for ciudad in ciudades]

        if form.is_valid():
            registro = Usuario(
                rut=form.cleaned_data['rut'],
                nombre=form.cleaned_data['nombre'],
                telefono=form.cleaned_data['telefono'],
                email=form.cleaned_data['email'],
                contraseña=make_password(form.cleaned_data['contraseña']),
                direccion=form.cleaned_data['direccion'],
                ciudad=form.cleaned_data['ciudad'],
                region=form.cleaned_data['region'],
            )
            registro.save()
            return redirect('home')
        else:
            print(form.errors)
            messages.error(request, "Hubo un error en el formulario.")
    data = {'form': form, 'regiones_ciudades': regiones_ciudades}
    return render(request, 'register.html', data)



def perfil(request):
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return redirect('login')
    
    usuario = get_object_or_404(Usuario, id=usuario_id)
    compras = Venta.objects.filter(usuario=usuario).order_by('-fecha')[:3]
    opiniones = Opinion.objects.filter(usuario=usuario).order_by('-fecha_creacion')[:2]
    reclamos_recientes = Reclamo.objects.filter(usuario=usuario).order_by('-fecha')[:2]
    
    return render(request, 'perfil_usuario.html', {
        'usuario': usuario,
        'compras': compras,
        'opiniones': opiniones,
        'reclamos_recientes': reclamos_recientes,
    })

def lista_opiniones(request):
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return redirect('login')

    usuario = get_object_or_404(Usuario, id=usuario_id)
    opiniones = Opinion.objects.filter(usuario=usuario).order_by('-fecha_creacion')

    return render(request, 'lista_opiniones.html', {'opiniones': opiniones})

def ver_compras(request):
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        messages.error(request, "Debes iniciar sesión para ver tus compras.")
        return redirect('login')
    
    usuario = get_object_or_404(Usuario, id=usuario_id)
    compras = Venta.objects.filter(usuario=usuario).prefetch_related(
        'producto_venta__producto'
    ).order_by('-fecha')

    return render(request, 'ver_compras.html', {'usuario': usuario, 'compras': compras})



def crear_reclamo(request, compra_id):
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        messages.error(request, "Debes iniciar sesión para agregar un reclamo.")
        return redirect('login')

    usuario = get_object_or_404(Usuario, id=usuario_id)
    compra = get_object_or_404(Venta, id=compra_id, usuario=usuario)

    if request.method == 'POST':
        asunto = request.POST.get('asunto', '').strip()
        descripcion = request.POST.get('descripcion', '').strip()

        if not asunto or not descripcion:
            messages.error(request, "Todos los campos son obligatorios.")
        else:
            Reclamo.objects.create(usuario=usuario, asunto=asunto, descripcion=descripcion)
            messages.success(request, "Reclamo creado con éxito.")
            return redirect('ver_compras')

    return render(request, 'crear_reclamo.html', {
        'compra': compra
    })

def lista_reclamos(request):
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        messages.error(request, "Debes iniciar sesión para acceder a tus reclamos.")
        return redirect('login')

    usuario = get_object_or_404(Usuario, id=usuario_id)
    todos_reclamos = Reclamo.objects.filter(usuario=usuario).order_by('-id')

    return render(request, 'lista_reclamos.html', {
        'todos_reclamos': todos_reclamos,
    })




def cambiar_contraseña(request):
    if request.method == 'POST':
        contraseña_actual = request.POST.get('contraseña_actual')
        nueva_contraseña = request.POST.get('nueva_contraseña')
        confirmar_contraseña = request.POST.get('confirmar_contraseña')
        usuario_id = request.session.get('usuario_id')
        if usuario_id:
            try:
                usuario = Usuario.objects.get(id=usuario_id)
                if not check_password(contraseña_actual, usuario.contraseña):
                    messages.error(request, "La contraseña actual no es correcta.")
                elif nueva_contraseña != confirmar_contraseña:
                    messages.error(request, "Las contraseñas no coinciden. Inténtelo nuevamente.")
                else:
                    usuario.contraseña = make_password(nueva_contraseña)
                    usuario.save()
                    messages.success(request, "Contraseña actualizada exitosamente.")
                    return redirect('perfil')
            except Usuario.DoesNotExist:
                messages.error(request, "Usuario no encontrado. Inténtelo más tarde.")
        else:
            messages.error(request, "Debes iniciar sesión para cambiar tu contraseña.")

    storage = get_messages(request)
    mensajes = [{'tipo': message.tags, 'texto': message.message} for message in storage]

    return render(request, 'cambiar_contrausu.html', {'mensajes_json': json.dumps(mensajes)})


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

    usuario = get_object_or_404(Usuario, id=usuario_id)
    carrito, created = Carrito.objects.get_or_create(usuario=usuario)

    producto = get_object_or_404(Producto, id=producto_id)

    cantidad = int(request.POST.get('cantidad', 1))

    item_carrito, item_created = ItemCarritoProducto.objects.get_or_create(
        carrito=carrito, producto=producto
    )

    if item_created:
        if cantidad <= producto.stock:
            item_carrito.cantidad = cantidad
            item_carrito.save()
        else:
            messages.error(request, f"Solo hay {producto.stock} unidades disponibles de {producto.nombre}.")
    else:
        if item_carrito.cantidad + cantidad <= producto.stock:
            item_carrito.cantidad += cantidad
            item_carrito.save()
        else:
            messages.error(request, f"Solo hay {producto.stock} unidades disponibles de {producto.nombre}.")

    return redirect('ver_carrito')

def eliminar_del_carrito(request, item_id):
    if request.method == 'POST':
        try:
            item = get_object_or_404(ItemCarritoProducto, id=item_id)
            carrito = item.carrito
            item.delete()

            total_items = sum(i.cantidad for i in carrito.items.all())
            total = carrito.total_carrito()

            return JsonResponse({
                'success': True,
                'total_items': total_items,
                'total': total,
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Método no permitido'})

def actualizar_cantidad_carrito(request):
    if request.method == 'POST':
        item_id = request.POST.get('item_id')
        nueva_cantidad = int(request.POST.get('cantidad', 1))

        item = get_object_or_404(ItemCarritoProducto, id=item_id)
        producto = item.producto

        if nueva_cantidad > producto.stock:
            return JsonResponse({
                'success': False,
                'error': f"Solo hay {producto.stock} unidades disponibles de {producto.nombre}."
            })

        if nueva_cantidad > 0:
            item.cantidad = nueva_cantidad
            item.save()
        else:
            item.delete()

        carrito = item.carrito
        total_items = sum(i.cantidad for i in carrito.items.all())
        total = carrito.total_carrito()

        return JsonResponse({
            'success': True,
            'total': total,
            'total_items': total_items,
        })

    return JsonResponse({'success': False})

def ver_carrito(request):
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return redirect('login')

    usuario = get_object_or_404(Usuario, id=usuario_id)
    carrito, created = Carrito.objects.get_or_create(usuario=usuario)

    total_items = sum(item.cantidad for item in carrito.items.all())

    return render(request, 'carrito.html', {
        'carrito': carrito,
        'productos': carrito.items.all(),
        'total': carrito.total_carrito(),
        'total_items': total_items,  
    })

def carrito(request):
    return render(request, 'carrito.html')

def lista_favoritos(request):
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        messages.error(request, "Debes iniciar sesión para acceder al perfil.")
        return redirect('login')

    usuario = get_object_or_404(Usuario, id=usuario_id)

    wishlist_items = Favorito.objects.filter(usuario=usuario)
    return render(request, 'favorite.html', {'wishlist_items': wishlist_items})

def agregar_favorito(request, producto_id):
    usuario_id = request.session.get('usuario_id')

    if not usuario_id:
        return redirect('login') 

    usuario = get_object_or_404(Usuario, id=usuario_id)
    producto = get_object_or_404(Producto, id=producto_id)
    favorito, created = Favorito.objects.get_or_create(usuario=usuario, producto=producto)

    if created:
        messages.success(request, f"El producto {producto.nombre} ha sido agregado a tus favoritos.")
    else:
        messages.info(request, f"El producto {producto.nombre} ya está en tus favoritos.")

    return redirect('lista_favorito')

@require_http_methods(["DELETE"])
def eliminar_favorito(request, item_id):
    favorito = get_object_or_404(Favorito, id=item_id)
    favorito.delete()
    return JsonResponse({'message': 'Artículo eliminado correctamente'}, status=200)






def seleccionar_envio(request, usuario_id):
    usuario = get_object_or_404(Usuario, id=usuario_id)
    carrito = usuario.carritos.last() 

    if not carrito or not carrito.items.exists():
        return redirect('carrito_vacio') 

    if request.method == 'POST':
        metodo_envio = request.POST.get('metodo_envio', 'tienda')
        direccion_envio = usuario.direccion if metodo_envio == 'domicilio' else None
        request.session['metodo_envio'] = metodo_envio
        request.session['direccion_envio'] = direccion_envio

        return redirect('seleccionar_pago', usuario_id=usuario_id)

    return render(request, 'seleccionar_envio.html', {'usuario': usuario, 'carrito': carrito})


def seleccionar_pago(request, usuario_id):
    usuario = get_object_or_404(Usuario, id=usuario_id)
    carrito = usuario.carritos.last()

    if not carrito or not carrito.items.exists():
        messages.error(request, "No hay productos en tu carrito.")
        return redirect('ver_carrito')

    subtotal = sum(item.cantidad * item.producto.precio for item in carrito.items.all())

    metodo_envio = request.session.get('metodo_envio', 'tienda')
    costo_envio = 0
    if metodo_envio == 'domicilio':
        costo_envio = 5000

    total = subtotal + costo_envio

    if request.method == 'POST':
        metodo_pago = request.POST.get('metodo_pago', 'tarjeta')

        if metodo_pago == "tarjeta":
            return redirect('compra_exitosa', usuario_id=usuario_id)

        messages.error(request, "Método de pago no válido.")
        return redirect('seleccionar_pago', usuario_id=usuario_id)

    return render(request, 'seleccionar_pago.html', {
        'usuario': usuario,
        'total': total,
    })







def compra_exitosa(request, usuario_id):
    usuario = get_object_or_404(Usuario, id=usuario_id)
    carrito = usuario.carritos.last()

    if not carrito or not carrito.items.exists():
        messages.error(request, "No hay productos en tu carrito.")
        return redirect('ver_carrito')

    metodo_envio = request.session.get('metodo_envio', 'tienda')
    direccion_envio = request.session.get('direccion_envio')  
    metodo_pago = request.session.get('metodo_pago', 'tarjeta')

    venta = Venta.objects.create(
        carrito=carrito,
        usuario=usuario,
        metodo_envio=metodo_envio,
        direccion_envio=direccion_envio, 
    )

    for item in carrito.items.all():
        ProductoVenta.objects.create(
            venta=venta,
            producto=item.producto,
            cantidad=item.cantidad,
            precio_unitario=item.producto.precio,
        )

    venta.calcular_total()
    carrito.items.all().delete()

    return render(request, 'compra_exitosa.html', {
        'venta': venta,
        'metodo_pago': metodo_pago,
    })




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