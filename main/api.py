from rest_framework import serializers, viewsets
from .models import Clientes

# --- SERIALIZER ---
class ClientesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Clientes
        fields = '__all__'  # incluye todos los campos


# --- VIEWSET ---
class ClientesViewSet(viewsets.ModelViewSet):
    queryset = Clientes.objects.all().order_by('id_cliente')
    serializer_class = ClientesSerializer
