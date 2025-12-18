from rest_framework import serializers, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.response import Response
from .models import Clientes, Pedidos, Detalles_pedidos, Producto

# ============================================================
# SERIALIZERS BASE
# ============================================================

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

# ============================================================
# SERIALIZADORES PERSONALIZADOS PARA PEDIDOS
# ============================================================

# ------------------------------------------------------------
#LISTA SIMPLIFICADA PARA TABLA PRINCIPAL
# ------------------------------------------------------------

class PedidoSimplificadoSerializer(serializers.ModelSerializer):
    nombre_cliente = serializers.CharField(source="cliente.nombre")
    apellido_cliente = serializers.CharField(source="cliente.apellido")
    email_cliente = serializers.CharField(source="cliente.email")
    telefono_cliente = serializers.CharField(source="cliente.telefono")

    class Meta:
        model = Pedidos
        fields = [
            "id_pedido",
            "nombre_cliente",
            "apellido_cliente",
            "email_cliente",
            "telefono_cliente",
            "estado",
        ]


# ------------------------------------------------------------
#DETALLE COMPLETO DE UN PEDIDO
# ------------------------------------------------------------

class PedidoDetalleSerializer(serializers.ModelSerializer):
    nombre_cliente = serializers.CharField(source="cliente.nombre")
    apellido_cliente = serializers.CharField(source="cliente.apellido")
    telefono_cliente = serializers.CharField(source="cliente.telefono")
    email_cliente = serializers.CharField(source="cliente.email")
    direccion_cliente = serializers.CharField(source="cliente.direccion")
    rut_cliente = serializers.CharField(source="cliente.rut")


    detalles = serializers.SerializerMethodField()

    class Meta:
        model = Pedidos

        fields = [
            "id_pedido",
            "fecha_inicio",
            "fecha_entrega",
            "fecha_termino",
            "estado",        
            "mensaje",
            "imagen",            
            "nombre_cliente",
            "apellido_cliente",
            "telefono_cliente",
            "email_cliente",
            "direccion_cliente",
            "rut_cliente",            
            "detalles",
        ]

    def get_detalles(self, obj):
        detalles = obj.detalles.select_related("producto").all()
        return [
            {
                "id_detalle": d.id_detalle,
                "producto": d.producto.nombre,
                "cantidad": d.cantidad,
                "subtotal": d.subtotal,
            }
            for d in detalles
        ]

# ============================================================
# VIEWSETS
# ============================================================

class ClientesViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Clientes.objects.all().order_by('id')
    serializer_class = ClientesSerializer


class PedidosViewSet(viewsets.ModelViewSet):    
    permission_classes = [IsAuthenticated]
    queryset = Pedidos.objects.all().order_by('id_pedido')
    serializer_class = PedidosSerializer


class DetallesPedidosViewSet(viewsets.ModelViewSet):    
    permission_classes = [IsAuthenticated]
    queryset = Detalles_pedidos.objects.all().order_by('id_detalle')
    serializer_class = DetallesPedidosSerializer


class ProductoViewSet(viewsets.ModelViewSet):    
    permission_classes = [IsAuthenticated]
    queryset = Producto.objects.all().order_by('id_producto')
    serializer_class = ProductoSerializer

# ============================================================
# ENDPOINTS PERSONALIZADOS
# ============================================================



# LISTA SIMPLIFICADA

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def pedidos_simplificados(request):
    pedidos = Pedidos.objects.select_related("cliente").all()
    serializer = PedidoSimplificadoSerializer(pedidos, many=True)
    return Response(serializer.data)


#DETALLE DE UN PEDIDO
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def pedido_detalle(request, id_pedido):

    try:
        pedido = Pedidos.objects.get(id_pedido=id_pedido)

    except Pedidos.DoesNotExist:
        return Response({"error": "Pedido no encontrado"}, status=404)


    serializer = PedidoDetalleSerializer(pedido)
    return Response(serializer.data)


