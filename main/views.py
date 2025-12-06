from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.core.mail import send_mail, EmailMessage
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

# ---------------------------
# LOGIN / LOGOUT
# ---------------------------

def login_view(request):
    if request.method == "POST":
        username_or_email = request.POST.get("username")
        password = request.POST.get("password")
        try:
            user_obj = User.objects.get(Q(username__iexact=username_or_email) | Q(email__iexact=username_or_email))
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
    return render(request, 'user_dashboard.html', {'username': request.user.username})

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
        messages.success(request, "Cliente creado.")
        return redirect('clientes_list')
    return render(request, 'clientes/clientes_form.html', {'form': form})

@login_required
@user_passes_test(is_admin)
def clientes_update(request, pk):
    cliente = get_object_or_404(Clientes, pk=pk)
    form = ClientesForm(request.POST or None, instance=cliente)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, "Cliente actualizado.")
        return redirect('clientes_list')
    return render(request, 'clientes/clientes_form.html', {'form': form})

@login_required
@user_passes_test(is_admin)
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
            stock_critico=request.POST.get('stock_critico', 0),
            margen_ganancia=request.POST.get('margen_ganancia', 0),
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
        for campo in ['nombre','tipo_producto','talla','color','precio_unitario','cantidad_stock',
                      'stock_critico','margen_ganancia','distribuidor','contacto_distribuidor']:
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
        messages.success(request, 'Producto eliminado.')
        return redirect('productos_list')
    return render(request, 'productos/productos_confirm_delete.html', {'producto': producto})


# ---------------------------
# PEDIDOS
# ---------------------------

@login_required
@user_passes_test(is_admin)
def pedidos_list(request):
    pedidos = Pedidos.objects.select_related('cliente').all()
    return render(request, 'pedidos/pedidos_list.html', {'pedidos': pedidos})

@login_required
@user_passes_test(is_admin)
def pedidos_create(request):
    form = PedidosForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, "Pedido creado.")
        return redirect('pedidos_list')
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
        messages.success(request, "Pedido actualizado.")
        return redirect('pedidos_list')
    return render(request, 'pedidos/pedidos_form.html', {'form': form})

@login_required
@user_passes_test(is_admin)
def pedidos_delete(request, pk):
    pedido = get_object_or_404(Pedidos, pk=pk)
    if request.method == 'POST':
        pedido.delete()
        messages.success(request, "Pedido eliminado.")
        return redirect('pedidos_list')
    return render(request, 'pedidos/pedidos_confirm_delete.html', {'pedido': pedido})


# ---------------------------
# VISTAS PARA PEDIDOS RÁPIDOS / USUARIO
# ---------------------------

def pedido_exitoso(request):
    return render(request, "quickorder_success.html")


@login_required
def user_quickorder(request):
    productos = Producto.objects.all()
    cliente, _ = Clientes.objects.get_or_create(email=request.user.email, defaults={'nombre': request.user.username})
    
    if request.method == "POST":
        producto_id = request.POST.get("producto")
        cantidad = int(request.POST.get("cantidad", 1))
        mensaje = request.POST.get("mensaje")
        imagen = request.FILES.get("imagen")

        producto = get_object_or_404(Producto, id_producto=producto_id)
        if cantidad > producto.cantidad_stock:
            messages.error(request, f"No puedes pedir {cantidad} unidades. Solo hay {producto.cantidad_stock} en stock.")
            return redirect("user_quickorder")

        total = Decimal(producto.precio_unitario) * cantidad
        pedido = Pedidos.objects.create(cliente=cliente, fecha_inicio=timezone.now(), estado="Pendiente", precio_total=total)
        Detalles_pedidos.objects.create(pedido=pedido, producto=producto, cantidad=cantidad, subtotal=total, email_usuario=cliente.email)
        producto.cantidad_stock -= cantidad
        producto.save()

        # Enviar correo
        email = EmailMessage(
            subject=f"Nuevo pedido rápido de {cliente.nombre}",
            body=f"Cliente: {cliente.nombre}\nProducto: {producto.nombre}\nCantidad: {cantidad}\nTotal: {total}\nMensaje: {mensaje or 'Sin mensaje'}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=["jtorresllr@gmail.com"]
        )
        if imagen:
            email.attach(imagen.name, imagen.read(), imagen.content_type)
        try: email.send()
        except: pass

        messages.success(request, "Tu pedido fue enviado.")
        return redirect("pedido_exitoso")

    return render(request, "user_quickorder.html", {"cliente": cliente, "productos": productos})
