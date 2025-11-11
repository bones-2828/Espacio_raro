from django.contrib import admin
from .models import Producto, Clientes

# Register your models here.

class ProductoAdmin(admin.ModelAdmin):
    list_display = ('id_producto', 'nombre', 'tipo_producto', 'precio_unitario', 'cantidad_stock', 'distribuidor')
    search_fields = ('nombre', 'tipo_producto', 'distribuidor')