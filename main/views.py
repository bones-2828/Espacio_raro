from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.core.mail import send_mail
from django.core.mail import EmailMessage
from io import BytesIO
from django.utils import timezone
from decimal import Decimal
from django.conf import settings
from .models import Clientes, Producto, Pedidos, Detalles_pedidos
from .forms import ClientesForm, PedidosForm, DetallePedidosForm, PedidoInvitadoForm

# ---------------------------
# VISTAS GENERALES DEL SITIO
# ---------------------------

def homepage(request):
    return render(request, "index.html")


def order(request):
    return render(request, "quickorder.html")


# ---------------------------
# AUTENTICACIÓN Y USUARIOS
# ---------------------------

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            if user.is_superuser or user.is_staff:
                return redirect("dashboard")
            else:
                return redirect("user_dashboard")
        else:
            messages.error(request, "Usuario o contraseña incorrectos")
    
    return render(request, "login.html")


def register_view(request):
    return render(request, "register.html")


def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if not username or not email or not password1 or not password2:
            messages.error(request, "Todos los campos son obligatorios.")
        elif password1 != password2:
            messages.error(request, "Las contraseñas no coinciden.")
        elif User.objects.filter(username=username).exists():
            messages.error(request, "El nombre de usuario ya existe.")
        elif User.objects.filter(email=email).exists():
            messages.error(request, "El correo electrónico ya está registrado.")
        else:
            user = User.objects.create_user(username=username, email=email, password=password1)
            user.save()
            messages.success(request, "Cuenta creada correctamente. Puedes iniciar sesión.")
            return redirect('login_view')

    return render(request, 'register.html')


def is_admin(user):
    return user.is_superuser or user.is_staff


@login_required
@user_passes_test(is_admin)
def dashboard(request):
    return render(request, "dashboard.html")


def logout_view(request):
    logout(request)
    return redirect('login_view')


@login_required
def user_dashboard(request):
    if request.user.is_superuser or request.user.is_staff:
        return redirect('dashboard')
    context = {'username': request.user.username}
    return render(request, 'user_dashboard.html', context)


# ---------------------------
# CRUD CLIENTES
# ---------------------------

@login_required
@user_passes_test(is_admin)
def clientes_list(request):
    clientes = Clientes.objects.all()
    return render(request, 'clientes/clientes_list.html', {'clientes': clientes})


@login_required
@user_passes_test(is_admin)
def clientes_detail(request, pk):
    cliente = get_object_or_404(Clientes, pk=pk)
    return render(request, 'clientes/clientes_detail.html', {'cliente': cliente})


@login_required
@user_passes_test(is_admin)
def clientes_create(request):
    form = ClientesForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, "Cliente creado correctamente.")
        return redirect('clientes_list')
    return render(request, 'clientes/clientes_form.html', {'form': form, 'titulo': 'Crear Cliente'})


@login_required
@user_passes_test(is_admin)
def clientes_update(request, pk):
    cliente = get_object_or_404(Clientes, pk=pk)
    form = ClientesForm(request.POST or None, instance=cliente)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, "Cliente actualizado correctamente.")
        return redirect('clientes_list')
    return render(request, 'clientes/clientes_form.html', {'form': form, 'titulo': 'Editar Cliente'})


@login_required
@user_passes_test(is_admin)
def clientes_delete(request, pk):
    cliente = get_object_or_404(Clientes, pk=pk)
    if request.method == 'POST':
        cliente.delete()
        messages.success(request, "Cliente eliminado correctamente.")
        return redirect('clientes_list')
    return render(request, 'clientes/clientes_confirm_delete.html', {'object': cliente})


# ---------------------------
# CRUD PRODUCTOS
# ---------------------------

@login_required
@user_passes_test(is_admin)
def productos_list(request):
    productos = Producto.objects.all()
    return render(request, 'productos/productos_list.html', {'productos': productos})


@login_required
@user_passes_test(is_admin)
def productos_create(request):
    if request.method == 'POST':
        producto = Producto(
            nombre=request.POST['nombre'],
            tipo_producto=request.POST['tipo_producto'],
            talla=request.POST.get('talla', ''),
            color=request.POST.get('color', ''),
            precio_unitario=request.POST['precio_unitario'],
            cantidad_stock=request.POST['cantidad_stock'],
            distribuidor=request.POST.get('distribuidor', ''),
            contacto_distribuidor=request.POST.get('contacto_distribuidor', '')
        )
        producto.save()
        messages.success(request, 'Producto creado correctamente.')
        return redirect('productos_list')
    return render(request, 'productos/productos_form.html')


@login_required
@user_passes_test(is_admin)
def productos_update(request, id_producto):
    producto = get_object_or_404(Producto, id_producto=id_producto)
    if request.method == 'POST':
        for campo in ['nombre', 'tipo_producto', 'talla', 'color', 'precio_unitario', 'cantidad_stock', 'distribuidor', 'contacto_distribuidor']:
            setattr(producto, campo, request.POST.get(campo, getattr(producto, campo)))
        producto.save()
        messages.success(request, 'Producto actualizado correctamente.')
        return redirect('productos_list')
    return render(request, 'productos/productos_form.html', {'producto': producto})


@login_required
@user_passes_test(is_admin)
def productos_delete(request, id_producto):
    producto = get_object_or_404(Producto, id_producto=id_producto)
    if request.method == 'POST':
        producto.delete()
        messages.success(request, 'Producto eliminado correctamente.')
        return redirect('productos_list')
    return render(request, 'productos/productos_confirm_delete.html', {'producto': producto})


# ---------------------------
# CRUD PEDIDOS
# ---------------------------

@login_required
@user_passes_test(is_admin)
def pedidos_list(request):
    pedidos = Pedidos.objects.select_related('cliente').all()
    return render(request, 'pedidos/pedidos_list.html', {'pedidos': pedidos})


@login_required
@user_passes_test(is_admin)
def pedidos_create(request):
    if request.method == 'POST':
        form = PedidosForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Pedido creado correctamente.")
            return redirect('pedidos_list')
    else:
        form = PedidosForm()
    return render(request, 'pedidos/pedidos_form.html', {'form': form})


@login_required
@user_passes_test(is_admin)
def pedidos_detail(request, pk):
    pedido = get_object_or_404(Pedidos, pk=pk)
    detalles = pedido.detalles.all()
    return render(request, 'pedidos/pedidos_detail.html', {'pedido': pedido, 'detalles': detalles})


@login_required
@user_passes_test(is_admin)
def pedidos_update(request, pk):
    pedido = get_object_or_404(Pedidos, pk=pk)
    form = PedidosForm(request.POST or None, instance=pedido)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, "Pedido actualizado correctamente.")
        return redirect('pedidos_list')
    return render(request, 'pedidos/pedidos_form.html', {'form': form})


@login_required
@user_passes_test(is_admin)
def pedidos_delete(request, pk):
    pedido = get_object_or_404(Pedidos, pk=pk)
    if request.method == 'POST':
        pedido.delete()
        messages.success(request, "Pedido eliminado correctamente.")
        return redirect('pedidos_list')
    return render(request, 'pedidos/pedidos_confirm_delete.html', {'pedido': pedido})


# ---------------------------
# CRUD DETALLES PEDIDOS
# ---------------------------

@login_required
@user_passes_test(is_admin)
def detalles_pedidos_list(request):
    detalles = Detalles_pedidos.objects.all()
    return render(request, 'detalles_pedidos/detalles_pedidos_list.html', {'detalles': detalles})


@login_required
@user_passes_test(is_admin)
def detalles_pedidos_create(request):
    form = DetallePedidosForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Detalle de pedido creado correctamente.")
        return redirect('detalles_pedidos_list')
    return render(request, 'detalles_pedidos/detalles_form.html', {'form': form})


@login_required
@user_passes_test(is_admin)
def detalles_pedidos_update(request, pk):
    detalle = get_object_or_404(Detalles_pedidos, pk=pk)
    form = DetallePedidosForm(request.POST or None, instance=detalle)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Detalle de pedido actualizado correctamente.')
        return redirect('detalles_pedidos_list')
    return render(request, 'detalles_pedidos/detalles_form.html', {'form': form})


@login_required
@user_passes_test(is_admin)
def detalles_pedidos_delete(request, pk):
    detalle = get_object_or_404(Detalles_pedidos, pk=pk)
    if request.method == 'POST':
        detalle.delete()
        messages.success(request, 'Detalle de pedido eliminado correctamente.')
        return redirect('detalles_pedidos_list')
    return render(request, 'detalles_pedidos/detalles_confirm_delete.html', {'detalle': detalle})


# ---------------------------
# PEDIDOS ANÓNIMOS
# ---------------------------

def guardar_detalle_pedido(request):
    if request.method == 'POST':
        fullName = request.POST.get('fullName')
        address = request.POST.get('address')
        email = request.POST.get('email')
        rut = request.POST.get('rut')
        message = request.POST.get('message')
        product = request.POST.get('productType')

        cliente_invitado, _ = Clientes.objects.get_or_create(
            email='invitado@demo.cl',
            defaults={'nombre': 'Invitado', 'apellido': 'Público', 'telefono': 'N/A'}
        )

        try:
            producto = Producto.objects.get(nombre__iexact=product)
        except Producto.DoesNotExist:
            return JsonResponse({'error': 'El producto no existe'}, status=400)

        pedido = Pedidos.objects.create(
            cliente=cliente_invitado,
            fecha_inicio=timezone.now().date(),
            estado='pendiente',
            precio_total=Decimal(producto.precio_unitario)
        )

        Detalles_pedidos.objects.create(
            pedido=pedido,
            producto=producto,
            cantidad=1,
            subtotal=producto.precio_unitario,
            email_usuario=email
        )

        # enviar correo
        try:
            send_mail(
                subject=f'Nuevo pedido recibido - {producto.nombre}',
                message=(
                    f"Pedido recibido desde el sitio web:\n\n"
                    f"Cliente: {fullName}\n"
                    f"Correo: {email}\n"
                    f"Dirección: {address}\n"
                    f"RUT: {rut}\n"
                    f"Producto: {producto.nombre}\n"
                    f"Mensaje adicional: {message}\n\n"
                    f"El pedido ha sido registrado correctamente."
                ),
                from_email='tuservidor@tudominio.cl',
                recipient_list=['destino@tudominio.cl'],
                fail_silently=False,
            )
        except Exception as e:
            print("Error al enviar correo:", e)

        return JsonResponse({'success': True, 'mensaje': 'Pedido guardado correctamente con email del usuario.'})

    return render(request, 'formulario_pedido.html')


def order(request):
    productos = Producto.objects.all()

    if request.method == 'POST':
        nombre = request.POST.get('nombre_completo')
        email_cliente = request.POST.get('email')
        rut = request.POST.get('rut')
        direccion = request.POST.get('direccion')
        producto_id = request.POST.get('producto')
        cantidad = request.POST.get('cantidad')
        mensaje = request.POST.get('mensaje')
        imagen = request.FILES.get('imagen')

        # Buscar el producto seleccionado
        producto = Producto.objects.get(id_producto=producto_id)

        # Crear el cuerpo del correo
        contenido = f"""
        📦 NUEVO PEDIDO RECIBIDO

        👤 Nombre: {nombre}
        📧 Correo: {email_cliente}
        🪪 RUT: {rut}
        🏠 Dirección: {direccion}

        🛍️ Producto: {producto.nombre} ({producto.tipo_producto})
        💰 Precio unitario: ${producto.precio_unitario}
        🔢 Cantidad: {cantidad}
        💵 Total: ${producto.precio_unitario * int(cantidad)}

        📝 Mensaje adicional:
        {mensaje if mensaje else '— Sin mensaje —'}
        """

        # Crear y configurar el correo
        email = EmailMessage(
            subject='Nuevo Pedido — Espacio Raro',
            body=contenido,
            from_email='tuservidor@gmail.com',  # cambia por tu correo del servidor
            to=['jtorresllr@gmail.com'],  # destinatario final
        )

        # Adjuntar imagen si el usuario la sube
        if imagen:
            email.attach(imagen.name, imagen.read(), imagen.content_type)

        # Enviar correo
        try:
            email.send()
            messages.success(request, '✅ Tu pedido fue enviado correctamente.')
        except Exception as e:
            messages.error(request, f'❌ Error al enviar el correo: {e}')

        return redirect('pedido_exitoso')

    return render(request, 'quickorder.html', {'productos': productos})


def pedido_exitoso(request):
    return render(request, "quickorder_success.html")



#pagina de cuentas de usuarios

def user_pedidos_list(request):
    """Lista de pedidos del usuario"""
    try:
        cliente = Clientes.objects.get(email=request.user.email)
        pedidos = Pedidos.objects.filter(cliente=cliente).order_by('-fecha_inicio')
    except Clientes.DoesNotExist:
        pedidos = []
    return render(request, 'user_pedidos_list.html', {'pedidos': pedidos})


@login_required
def user_pedido_detail(request, pk):
    """Detalle de un pedido del usuario"""
    try:
        cliente = Clientes.objects.get(email=request.user.email)
        pedido = Pedidos.objects.get(pk=pk, cliente=cliente)
        detalles = pedido.detalles.all()  # usa related_name="detalles" en tu modelo
    except (Clientes.DoesNotExist, Pedidos.DoesNotExist):
        return redirect('user_pedidos_list')
    
    return render(request, 'user_pedido_detail.html', {
        'pedido': pedido,
        'detalles': detalles
    })


@login_required
def user_perfil_edit(request):
    """Editar perfil del usuario"""
    try:
        cliente = Clientes.objects.get(email=request.user.email)
    except Clientes.DoesNotExist:
        # Si el cliente no existe, crearlo automáticamente
        cliente = Clientes.objects.create(
            nombre=request.user.username,
            email=request.user.email
        )
    
    if request.method == "POST":
        cliente.nombre = request.POST.get('nombre', cliente.nombre)
        cliente.apellido = request.POST.get('apellido', cliente.apellido)
        cliente.rut = request.POST.get('rut', cliente.rut)  # ✅ ahora se puede editar el RUT
        cliente.telefono = request.POST.get('telefono', cliente.telefono)
        cliente.direccion = request.POST.get('direccion', cliente.direccion)
        # El email no se cambia aquí para mantener integridad
        cliente.save()
        messages.success(request, "✅ Perfil actualizado correctamente.")
        return redirect('user_dashboard')
    
    return render(request, 'user_perfil_edit.html', {'cliente': cliente})



@login_required
def user_quickorder(request):
    """
    Permite a un cliente logueado realizar un pedido rápido con su cuenta.
    Muestra los datos del cliente, permite seleccionar producto y cantidad,
    y envía un correo con la información del pedido, además de registrarlo en la BD.
    """
    try:
        cliente = Clientes.objects.get(email=request.user.email)
    except Clientes.DoesNotExist:
        messages.error(request, "No se encontró tu perfil de cliente. Contacta al administrador.")
        return redirect('user_dashboard')

    productos = Producto.objects.all()

    if request.method == "POST":
        producto_id = request.POST.get("producto")
        cantidad = int(request.POST.get("cantidad", 1))
        mensaje = request.POST.get("mensaje")
        imagen = request.FILES.get("imagen")

        # Obtener producto
        try:
            producto = Producto.objects.get(id_producto=producto_id)
        except Producto.DoesNotExist:
            messages.error(request, "El producto seleccionado no existe.")
            return redirect("user_quickorder")

        # Calcular total
        total = Decimal(producto.precio_unitario) * cantidad

        # Crear el pedido
        pedido = Pedidos.objects.create(
            cliente=cliente,
            fecha_inicio=timezone.now(),
            estado="Pendiente",
            precio_total=total
        )

        # Crear el detalle del pedido
        Detalles_pedidos.objects.create(
            pedido=pedido,
            producto=producto,
            cantidad=cantidad,
            subtotal=total,
            email_usuario=cliente.email
        )

        # Construir el contenido del correo
        subject = f"Nuevo pedido rápido de {cliente.nombre}"
        body = f"""
        📦 NUEVO PEDIDO RÁPIDO

        👤 Cliente: {cliente.nombre}
        📧 Correo: {cliente.email}
        🪪 RUT: {cliente.rut or 'No registrado'}
        🏠 Dirección: {cliente.direccion or 'No registrada'}

        🛍️ Producto: {producto.nombre} ({producto.tipo_producto})
        💰 Precio unitario: ${producto.precio_unitario}
        🔢 Cantidad: {cantidad}
        💵 Total: ${total}

        📝 Mensaje adicional:
        {mensaje or '— Sin mensaje —'}

        🕓 Fecha del pedido: {pedido.fecha_inicio.strftime('%d/%m/%Y %H:%M:%S')}
        """

        # Configurar el correo
        email = EmailMessage(
            subject=subject,
            body=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=["jtorresllr@gmail.com"],  # destino del correo
        )

        # Adjuntar imagen si existe
        if imagen:
            email.attach(imagen.name, imagen.read(), imagen.content_type)

        # Enviar el correo
        try:
            email.send()
            messages.success(request, "✅ Tu pedido fue enviado correctamente.")
        except Exception as e:
            messages.warning(request, f"⚠️ El pedido se guardó, pero no se pudo enviar el correo: {e}")

        return redirect("pedido_exitoso")

    # Mostrar formulario
    return render(request, "user_quickorder.html", {
        "cliente": cliente,
        "productos": productos
    })



@login_required
def user_confirm(request):
    """
    Muestra los datos del cliente logueado para su confirmación.
    No permite editar, solo visualizar.
    """
    try:
        cliente = Clientes.objects.get(email=request.user.email)
    except Clientes.DoesNotExist:
        messages.error(request, "No se encontró tu perfil de cliente.")
        return redirect("user_dashboard")

    return render(request, "user_confirm.html", {"cliente": cliente})
