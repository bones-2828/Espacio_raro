from django.db import models
from django.core.mail import send_mail
from django.conf import settings
from decimal import Decimal


class Clientes(models.Model):
    id_cliente = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=25)
    apellido = models.CharField(max_length=25, blank=True, null=True)
    email = models.EmailField(unique=True)
    telefono = models.CharField(max_length=12, blank=True, null=True)
    direccion = models.CharField(max_length=100, blank=True, null=True)
    rut = models.CharField(max_length=12, unique=True)

    def __str__(self):
        return f"{self.nombre} {self.apellido or ''}".strip()


class Producto(models.Model):
    id_producto = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    tipo_producto = models.CharField(max_length=100)
    talla = models.CharField(max_length=50, blank=True, null=True)
    color = models.CharField(max_length=20, blank=True, null=True)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    cantidad_stock = models.IntegerField(default=0)
    distribuidor = models.CharField(max_length=30, blank=True, null=True)
    contacto_distribuidor = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return self.nombre


class Pedidos(models.Model):
    id_pedido = models.AutoField(primary_key=True)
    cliente = models.ForeignKey(Clientes, on_delete=models.CASCADE, related_name="pedidos")
    fecha_inicio = models.DateTimeField(auto_now_add=True)
    fecha_entrega = models.DateField(blank=True, null=True)
    fecha_termino = models.DateField(blank=True, null=True)
    estado = models.CharField(max_length=50, default="Pendiente")  # 👈 valor coherente con la vista
    precio_total = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    mensaje = models.TextField(blank=True, null=True)
    imagen = models.ImageField(upload_to="imagenes_pedidos/", blank=True, null=True)

    def __str__(self):
        return f"Pedido #{self.id_pedido} - {self.cliente.nombre}"

    def enviar_email_confirmacion(self):
        """Envía un correo con los detalles del pedido"""
        detalles = self.detalles.all()
        productos = ", ".join([f"{d.producto.nombre} (x{d.cantidad})" for d in detalles]) or "Sin productos registrados"

        subject = f"Nuevo pedido recibido #{self.id_pedido}"
        message = (
            f"Cliente: {self.cliente.nombre} {self.cliente.apellido or ''}\n"
            f"Correo: {self.cliente.email}\n"
            f"Dirección: {self.cliente.direccion or '(no especificada)'}\n"
            f"RUT: {self.cliente.rut}\n"
            f"Productos: {productos}\n"
            f"Total: ${self.precio_total}\n"
            f"Mensaje: {self.mensaje or '(sin mensaje)'}\n"
            f"Estado: {self.estado}\n"
            f"Fecha del pedido: {self.fecha_inicio.strftime('%d/%m/%Y %H:%M')}"
        )

        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            ["jtorresllr@gmail.com"],  # 👈 cámbialo por tu correo real
            fail_silently=False,
        )


class Detalles_pedidos(models.Model):
    id_detalle = models.AutoField(primary_key=True)
    pedido = models.ForeignKey(Pedidos, on_delete=models.CASCADE, related_name="detalles")
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    email_usuario = models.EmailField(null=True, blank=True)

    def __str__(self):
        return f"Detalle #{self.id_detalle} - Pedido {self.pedido.id_pedido}"

    def save(self, *args, **kwargs):
        """Actualiza subtotal automáticamente y recalcula total del pedido"""
        if self.producto and not self.subtotal:
            self.subtotal = Decimal(self.cantidad) * self.producto.precio_unitario
        super().save(*args, **kwargs)

        # actualizar total del pedido
        total = sum(det.subtotal for det in self.pedido.detalles.all())
        self.pedido.precio_total = total
        self.pedido.save(update_fields=["precio_total"])
