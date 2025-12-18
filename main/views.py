from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
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
# VISTAS GENERALES
# ---------------------------

def homepage(request):
    return render(request, "index.html")

def contactos(request):
    return render(request, "contactos.html")

def order(request):
    return render(request, "quickorder.html")


# ---------------------------
# LOGIN / LOGOUT
# ---------------------------

def login_view(request):
    if request.method == "POST":
        username_or_email = request.POST.get("username")
        password = request.POST.get("password")

        try:
            user_obj = User.objects.get(
                Q(username__iexact=username_or_email) | Q(email__iexact=username_or_email)
            )
            username = user_obj.username
        except User.DoesNotExist:
            username = username_or_email  

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            if user.is_superuser or user.is_staff:
                return redirect("dashboard")
            else:
                return redirect("user_dashboard")
        else:
            messages.error(request, "Usuario/Email o contraseña incorrectos.")
    
    return render(request, "login.html")


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
            messages.error(request, "El correo ya está registrado.")
        else:
            User.objects.create_user(username=username, email=email, password=password1)
            messages.success(request, "Cuenta creada correctamente.")
            return redirect('login_view')

    return render(request, 'register.html')


def is_admin(user):
    return user.is_authenticated and user.is_superuser


@login_required(login_url='login_view')
@user_passes_test(is_admin, login_url='login_view')
def dashboard(request):

    #print para verificar problema
    print("AUTH:", request.META.get("HTTP_AUTHORIZATION"))


    # Protección extra (defensa en profundidad)

    if not request.user.is_authenticated or not is_admin(request.user):
        return redirect('login_view')

    return render(request, "dashboard.html")



def logout_view(request):
    logout(request)
    request.session.flush()
    return redirect('homepage')


@login_required
def user_dashboard(request):
    if request.user.is_superuser or request.user.is_staff:
        return redirect('dashboard')
    return render(request, 'user_dashboard.html', {'username': request.user.username})


# ---------------------------
# CRUD CLIENTES
# ---------------------------

@login_required(login_url='login_view')
@user_passes_test(is_admin, login_url='login_view')
def clientes_list(request):
    clientes = Clientes.objects.all()
    return render(request, 'clientes/clientes_list.html', {'clientes': clientes})


@login_required(login_url='login_view')
@user_passes_test(is_admin, login_url='login_view')
def clientes_detail(request, pk):
    cliente = get_object_or_404(Clientes, pk=pk)
    return render(request, 'clientes/clientes_detail.html', {'cliente': cliente})


@login_required(login_url='login_view')
@user_passes_test(is_admin, login_url='login_view')
def clientes_create(request):
    form = ClientesForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, "Cliente creado.")
        return redirect('clientes_list')
    return render(request, 'clientes/clientes_form.html', {'form': form})


@login_required(login_url='login_view')
@user_passes_test(is_admin, login_url='login_view')
def clientes_update(request, pk):
    cliente = get_object_or_404(Clientes, pk=pk)
    form = ClientesForm(request.POST or None, instance=cliente)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, "Cliente actualizado.")
        return redirect('clientes_list')
    return render(request, 'clientes/clientes_form.html', {'form': form})


@login_required(login_url='login_view')
@user_passes_test(is_admin, login_url='login_view')
def clientes_delete(request, pk):
    cliente = get_object_or_404(Clientes, pk=pk)
    if request.method == 'POST':
        cliente.delete()
        messages.success(request, "Cliente eliminado.")
        return redirect('clientes_list')
    return render(request, 'clientes/clientes_confirm_delete.html', {'object': cliente})


# ---------------------------
# CRUD PRODUCTOS
# ---------------------------

@login_required(login_url='login_view')
@user_passes_test(is_admin, login_url='login_view')
def productos_list(request):
    productos = Producto.objects.all()
    return render(request, 'productos/productos_list.html', {'productos': productos})


@login_required(login_url='login_view')
@user_passes_test(is_admin, login_url='login_view')
def productos_create(request):
    if request.method == 'POST':
        producto = Producto(
            nombre=request.POST['nombre'],
            tipo_producto=request.POST['tipo_producto'],
            talla=request.POST.get('talla') or None,
            color=request.POST.get('color') or None,
            precio_unitario=request.POST['precio_unitario'],
            cantidad_stock=request.POST['cantidad_stock'],

            stock_critico=(
                int(request.POST['stock_critico'])
                if request.POST.get('stock_critico')
                else None
            ),
            margen_ganancia=(
                int(request.POST['margen_ganancia'])
                if request.POST.get('margen_ganancia')
                else None
            ),

            distribuidor=request.POST.get('distribuidor', ''),
            contacto_distribuidor=request.POST.get('contacto_distribuidor', '')
        )
        producto.save()
        messages.success(request, 'Producto creado correctamente.')
        return redirect('productos_list')

    return render(request, 'productos/productos_form.html')


@login_required(login_url='login_view')
@user_passes_test(is_admin, login_url='login_view')
def productos_update(request, id_producto):
    producto = get_object_or_404(Producto, id_producto=id_producto)

    if request.method == 'POST':

        producto.nombre = request.POST['nombre']
        producto.tipo_producto = request.POST['tipo_producto']
        producto.talla = request.POST.get('talla') or None
        producto.color = request.POST.get('color') or None
        producto.precio_unitario = request.POST['precio_unitario']
        producto.cantidad_stock = request.POST['cantidad_stock']        
        stock_critico = request.POST.get('stock_critico')
        producto.stock_critico = stock_critico if stock_critico else None
        margen = request.POST.get('margen_ganancia')
        producto.margen_ganancia = margen if margen else None
        producto.distribuidor = request.POST.get('distribuidor') or None
        producto.contacto_distribuidor = request.POST.get('contacto_distribuidor') or None

        producto.save()
        messages.success(request, 'Producto actualizado correctamente.')
        return redirect('productos_list')

    return render(request, 'productos/productos_form.html', {'producto': producto})


@login_required(login_url='login_view')
@user_passes_test(is_admin, login_url='login_view')
def productos_delete(request, id_producto):
    producto = get_object_or_404(Producto, id_producto=id_producto)
    if request.method == 'POST':
        producto.delete()
        messages.success(request, 'Producto eliminado.')
        return redirect('productos_list')
    return render(request, 'productos/productos_confirm_delete.html', {'producto': producto})


# ---------------------------
# CRUD PEDIDOS
# ---------------------------

@login_required(login_url='login_view')
@user_passes_test(is_admin, login_url='login_view')
def pedidos_list(request):
    pedidos = Pedidos.objects.select_related('cliente').all()
    return render(request, 'pedidos/pedidos_list.html', {'pedidos': pedidos})


@login_required(login_url='login_view')
@user_passes_test(is_admin, login_url='login_view')
def pedidos_create(request):
    form = PedidosForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, "Pedido creado.")
        return redirect('pedidos_list')
    return render(request, 'pedidos/pedidos_form.html', {'form': form})


@login_required(login_url='login_view')
@user_passes_test(is_admin, login_url='login_view')
def pedidos_detail(request, pk):
    pedido = get_object_or_404(Pedidos, pk=pk)
    detalles = pedido.detalles.all()
    return render(request, 'pedidos/pedidos_detail.html', {'pedido': pedido, 'detalles': detalles})


@login_required(login_url='login_view')
@user_passes_test(is_admin, login_url='login_view')
def pedidos_update(request, pk):
    pedido = get_object_or_404(Pedidos, pk=pk)
    form = PedidosForm(request.POST or None, instance=pedido)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, "Pedido actualizado.")
        return redirect('pedidos_list')
    return render(request, 'pedidos/pedidos_form.html', {'form': form})


@login_required(login_url='login_view')
@user_passes_test(is_admin, login_url='login_view')
def pedidos_delete(request, pk):
    pedido = get_object_or_404(Pedidos, pk=pk)
    if request.method == 'POST':
        pedido.delete()
        messages.success(request, "Pedido eliminado.")
        return redirect('pedidos_list')
    return render(request, 'pedidos/pedidos_confirm_delete.html', {'pedido': pedido})


# ---------------------------
# CRUD DETALLES PEDIDOS
# ---------------------------

@login_required(login_url='login_view')
@user_passes_test(is_admin, login_url='login_view')
def detalles_pedidos_list(request):
    detalles = Detalles_pedidos.objects.all()
    return render(request, 'detalles_pedidos/detalles_pedidos_list.html', {'detalles': detalles})


@login_required(login_url='login_view')
@user_passes_test(is_admin, login_url='login_view')
def detalles_pedidos_create(request):
    form = DetallePedidosForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Detalle creado.")
        return redirect('detalles_pedidos_list')
    return render(request, 'detalles_pedidos/detalles_form.html', {'form': form})


@login_required(login_url='login_view')
@user_passes_test(is_admin, login_url='login_view')
def detalles_pedidos_update(request, pk):
    detalle = get_object_or_404(Detalles_pedidos, pk=pk)
    form = DetallePedidosForm(request.POST or None, instance=detalle)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Detalle actualizado.')
        return redirect('detalles_pedidos_list')
    return render(request, 'detalles_pedidos/detalles_form.html', {'form': form})


@login_required(login_url='login_view')
@user_passes_test(is_admin, login_url='login_view')
def detalles_pedidos_delete(request, pk):
    detalle = get_object_or_404(Detalles_pedidos, pk=pk)
    if request.method == 'POST':
        detalle.delete()
        messages.success(request, 'Detalle eliminado.')
        return redirect('detalles_pedidos_list')
    return render(request, 'detalles_pedidos/detalles_confirm_delete.html', {'detalle': detalle})


# ---------------------------
# CRUD SUPERUSUARIOS
# ---------------------------

def superuser_required(view_func):
    return user_passes_test(lambda u: u.is_superuser)(view_func)


@superuser_required
def superuser_list(request):
    superusers = User.objects.filter(is_superuser=True)
    return render(request, 'superusers/superuser_list.html', {'superusers': superusers})


@superuser_required
def superuser_create(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")

        if not username or not password:
            messages.error(request, "Debe ingresar usuario y contraseña.")
        else:
            User.objects.create_superuser(username=username, email=email, password=password)
            messages.success(request, f"Superusuario '{username}' creado.")
            return redirect('superuser_list')

    return render(request, 'superusers/superuser_create.html')


@superuser_required
def superuser_delete(request, pk):
    superuser = get_object_or_404(User, pk=pk)
    if request.user == superuser:
        messages.error(request, "No puedes eliminar tu propio usuario.")
    else:
        superuser.delete()
        messages.success(request, f"Superusuario '{superuser.username}' eliminado.")
    return redirect('superuser_list')


# ---------------------------
# PEDIDOS ANÓNIMOS
# ---------------------------

def guardar_detalle_pedido(request):
    if request.method == 'POST':
        full_name = request.POST.get('fullName')
        address = request.POST.get('address')
        email = request.POST.get('email')
        rut = request.POST.get('rut')
        message = request.POST.get('message')
        product = request.POST.get('productType')

        cliente, _ = Clientes.objects.get_or_create(
            email=email,
            defaults={
                'nombre': full_name,
                'telefono': 'N/A',
                'direccion': address,
                'rut': rut
            }
        )

        producto = get_object_or_404(Producto, nombre__iexact=product)

        pedido = Pedidos.objects.create(
            cliente=cliente,
            estado="Pendiente de manufacturar"
        )

        Detalles_pedidos.objects.create(
            pedido=pedido,
            producto=producto,
            cantidad=1,
            subtotal=producto.precio_unitario,
            email_usuario=email
        )

        return JsonResponse({'success': True})

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

        try:
            producto = Producto.objects.get(id_producto=producto_id)
            cantidad = int(cantidad)
            if cantidad < 1:
                raise ValueError
        except:
            messages.error(request, "Producto o cantidad inválidos.")
            return redirect('quickorder')

        if cantidad > producto.cantidad_stock:
            messages.error(
                request,
                f"No hay stock suficiente ({producto.cantidad_stock})."
            )
            return redirect('quickorder')

        cliente, _ = Clientes.objects.get_or_create(
            email=email_cliente,
            defaults={
                'nombre': nombre,
                'rut': rut,
                'telefono': 'N/A',
                'direccion': direccion
            }
        )

        pedido = Pedidos.objects.create(
            cliente=cliente,
            estado="Pendiente de manufacturar"
        )

        subtotal = Decimal(producto.precio_unitario) * cantidad

        Detalles_pedidos.objects.create(
            pedido=pedido,
            producto=producto,
            cantidad=cantidad,
            subtotal=subtotal,
            email_usuario=email_cliente
        )

        producto.cantidad_stock -= cantidad
        producto.save()

        messages.success(request, "Pedido realizado correctamente.")
        return redirect('pedido_exitoso')

    return render(request, 'quickorder.html', {'productos': productos})



def pedido_exitoso(request):
    return render(request, "quickorder_success.html")



@login_required(login_url='login_view')
def user_order_success(request):
    return render(request, "user_order_success.html")



@login_required(login_url='login_view')
def user_pedidos_list(request):
    try:
        cliente = Clientes.objects.get(email=request.user.email)
        pedidos = Pedidos.objects.filter(cliente=cliente).order_by('-fecha_inicio')
    except Clientes.DoesNotExist:
        pedidos = []

    return render(request, 'user_pedidos_list.html', {'pedidos': pedidos})



@login_required(login_url='login_view')
def user_pedido_detail(request, pk):
    cliente = get_object_or_404(Clientes, email=request.user.email)
    pedido = get_object_or_404(Pedidos, pk=pk, cliente=cliente)
    detalles = pedido.detalles.all()

    return render(request, 'user_pedido_detail.html', {
        'pedido': pedido,
        'detalles': detalles
    })



@login_required(login_url='login_view')
def user_perfil_edit(request):
    cliente, _ = Clientes.objects.get_or_create(
        email=request.user.email,
        defaults={'nombre': request.user.username}
    )

    if request.method == "POST":
        cliente.nombre = request.POST.get('nombre', cliente.nombre)
        cliente.apellido = request.POST.get('apellido', cliente.apellido)
        cliente.rut = request.POST.get('rut', cliente.rut)
        cliente.telefono = request.POST.get('telefono', cliente.telefono)
        cliente.direccion = request.POST.get('direccion', cliente.direccion)
        cliente.save()

        messages.success(request, "Perfil actualizado.")
        return redirect('user_dashboard')

    return render(request, 'user_perfil_edit.html', {'cliente': cliente})



@login_required(login_url='login_view')
def user_quickorder(request):
    cliente = get_object_or_404(Clientes, email=request.user.email)
    productos = Producto.objects.all()

    if request.method == "POST":
        producto_id = request.POST.get("producto")
        cantidad = int(request.POST.get("cantidad", 1))
        mensaje = request.POST.get("mensaje")
        imagen = request.FILES.get("imagen")

        producto = get_object_or_404(Producto, id_producto=producto_id)

        if cantidad > producto.cantidad_stock:
            messages.error(
                request,
                f"No hay stock suficiente ({producto.cantidad_stock})."
            )
            return redirect("user_quickorder")

        pedido = Pedidos.objects.create(
            cliente=cliente,
            estado="Pendiente de manufacturar"
        )

        subtotal = Decimal(producto.precio_unitario) * cantidad

        Detalles_pedidos.objects.create(
            pedido=pedido,
            producto=producto,
            cantidad=cantidad,
            subtotal=subtotal,
            email_usuario=cliente.email
        )

        producto.cantidad_stock -= cantidad
        producto.save()

        messages.success(request, "Pedido realizado correctamente.")
        return redirect("user_order_success")

    return render(request, "user_quickorder.html", {
        "cliente": cliente,
        "productos": productos
    })




@login_required(login_url='login_view')
def user_confirm(request):
    cliente = get_object_or_404(Clientes, email=request.user.email)
    return render(request, "user_confirm.html", {"cliente": cliente})








