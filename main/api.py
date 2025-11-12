from rest_framework import serializers, viewsets
from .models import Clientes, Pedidos, Detalles_pedidos, Producto

# --- SERIALIZER ---        
class ClientesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Clientes
        fields = '__all__'

class PedidosSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pedidos
        fields = '__all__'
        
class DetallesPedidosSerializer(serializers.ModelSerializer):
    class Meta:
        model = Detalles_pedidos
        fields = '__all__'

class ProductoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Producto
        fields = '__all__'


# --- VIEWSET ---
class ClientesViewSet(viewsets.ModelViewSet):
    queryset = Clientes.objects.all().order_by('id_cliente')
    serializer_class = ClientesSerializer

class PedidosViewSet(viewsets.ModelViewSet):
    queryset = Pedidos.objects.all().order_by('id_pedido')
    serializer_class = PedidosSerializer
    
class DetallesPedidosViewSet(viewsets.ModelViewSet):
    queryset = Detalles_pedidos.objects.all().order_by('id_detalle')
    serializer_class = DetallesPedidosSerializer

class ProductoViewSet(viewsets.ModelViewSet):
    queryset = Producto.objects.all().order_by('id_producto')
    serializer_class = ProductoSerializer