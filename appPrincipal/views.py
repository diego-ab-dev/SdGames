from django.shortcuts import render, get_object_or_404, redirect
from .models import Producto ,ItemCarritoProducto, Usuario, Carrito, Venta
from appPrincipal import forms
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.http import JsonResponse, Http404, HttpResponse
from django.db.models import Avg
from django.contrib.auth.hashers import make_password, check_password
from django.conf import settings
import mercadopago
import json
from django.core.mail import send_mail
from django.utils.crypto import get_random_string
# Create your views here.
def password_reset_request(request):
    if request.method == 'POST':
        form = forms.PasswordResetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                usuario = Usuario.objects.get(email=email)
                # Generar un token único (podría ser un link seguro en una implementación más compleja)
                token = get_random_string(length=32)
                usuario.contraseña = make_password(token)
                usuario.save()

                # Enviar el correo
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
    messages.success(request, "Sesión cerrada exitosamente.")
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
    return render(request, 'favorite.html')


def detalles_compra(request):
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return redirect('login') 

    usuario = get_object_or_404(Usuario, id=usuario_id)
    carrito = get_object_or_404(Carrito, usuario=usuario)

    if request.method == 'POST':
        metodo_envio = request.POST.get('metodo_envio')
        direccion_envio = usuario.direccion if metodo_envio == 'domicilio' else "Retiro en tienda"

        venta = Venta.objects.create(
            usuario=usuario,
            metodo_envio=metodo_envio,
            direccion_envio=direccion_envio,
            estado='Pendiente',
            carrito=carrito
        )


        venta.productos.set(carrito.items.all())

        venta.subtotal = sum(item.producto.precio * item.cantidad for item in carrito.items.all())

        venta.envio = 0 if metodo_envio == 'tienda' else 5000

        venta.total = venta.subtotal + venta.envio

        venta.save()
        carrito.save()

        return redirect('pago') 

    return render(request, 'detalles_compra.html', {
        'usuario': usuario,
        'carrito': carrito,
        'productos': carrito.items.all(),
        'total': carrito.total_carrito(),
    })


def pago(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            metodo = data.get('metodo_pago')
            total = data.get('total')

            usuario_id = request.session.get('usuario_id')
            if not usuario_id:
                return JsonResponse({'error': 'Usuario no autenticado'}, status=403)

            usuario = get_object_or_404(Usuario, id=usuario_id)
            carrito = get_object_or_404(Carrito, usuario=usuario)

            if metodo == 'mercado_pago':
                sdk = mercadopago.SDK(settings.MERCADO_PAGO_ACCESS_TOKEN)
                preference_data = {
                    "items": [
                        {
                            "title": "Compra en SD Games",
                            "quantity": 1,
                            "currency_id": "CLP",
                            "unit_price": float(total),
                        }
                    ],
                    "back_urls": {
                        "success": request.build_absolute_uri('/pago-exitoso/'),
                        "failure": request.build_absolute_uri('/pago-fallido/'),
                        "pending": request.build_absolute_uri('/pago-pendiente/'),
                    },
                    "auto_return": "approved",
                    "external_reference": str(carrito.id),  # Referencia única
                }

                preference_response = sdk.preference().create(preference_data)

                return JsonResponse({
                    'mensaje': 'Redirigiendo a Mercado Pago...',
                    'redirect_url': preference_response["response"]["init_point"],
                })

            return JsonResponse({'mensaje': 'Método de pago no soportado'}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Datos mal formados'}, status=400)

    elif request.method == 'GET':
        total = float(request.GET.get('total', 0))
        return render(request, 'pago.html', {'total': total})

    return JsonResponse({'error': 'Método no permitido'}, status=405)



def pago_exitoso(request):
    return render(request, 'pago_exitoso.html')

def pago_fallido(request):
    return render(request, 'pago_fallido.html', {'mensaje': 'Hubo un problema con tu pago. Por favor, intenta nuevamente.'})

def pago_pendiente(request):
    return render(request, 'pago_pendiente.html', {'mensaje': 'Tu pago está pendiente de aprobación. Recibirás una notificación cuando sea confirmado.'})



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