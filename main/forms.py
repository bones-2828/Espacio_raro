from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.forms import inlineformset_factory
from .models import Clientes, Pedidos, Detalles_pedidos


# ---------- FORMULARIO BASE CON ESTILO ----------
class BaseStyledForm(forms.ModelForm):
    """Aplica clases CSS automáticamente a todos los campos del formulario."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.Select):
                field.widget.attrs.update({'class': 'form-select'})
            else:
                field.widget.attrs.update({'class': 'form-control'})


# ---------- FORMULARIO DE REGISTRO DE USUARIOS ----------
class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Correo electrónico'})
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': 'Usuario'}),
            'password1': forms.PasswordInput(attrs={'placeholder': 'Contraseña'}),
            'password2': forms.PasswordInput(attrs={'placeholder': 'Confirmar contraseña'}),
        }


# ---------- FORMULARIO CLIENTES ----------
class ClientesForm(BaseStyledForm):
    class Meta:
        model = Clientes
        fields = ['nombre', 'apellido', 'email', 'telefono', 'direccion', 'rut']



# ---------- FORMULARIO PEDIDOS ----------
class PedidosForm(forms.ModelForm):
    
    ESTADOS_PEDIDO = [
            ('Pendiente de manufacturar', 'Pendiente de manufacturar'),
            ('En proceso de manufactura', 'En proceso de manufactura'),
            ('Listo para entregar', 'Listo para entregar'),
            ('Pedido entregado', 'Pedido entregado'),
            ('Archivado', 'Archivado'),
            ('Pedido cancelado', 'Pedido cancelado')
        ]

    estado = forms.ChoiceField(
            choices=ESTADOS_PEDIDO,
            widget=forms.Select(attrs={'class':'form-control'})
        )


    class Meta:
        model = Pedidos
        fields = '__all__'
        widgets = {
            'cliente': forms.Select(attrs={'class': 'form-control'}),
            'fecha_inicio': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'fecha_entrega': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'fecha_termino': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),                        
            'mensaje': forms.Textarea(attrs={'class': 'form-control'}),
            'imagen': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }


# ---------- FORMULARIO DETALLES DE PEDIDO ----------
class DetallePedidosForm(BaseStyledForm):
    class Meta:
        model = Detalles_pedidos
        fields = ['pedido', 'producto', 'cantidad', 'subtotal', 'email_usuario']  # 👈 nuevo campo
        widgets = {
            'pedido': forms.Select(attrs={'class': 'form-select'}),
            'producto': forms.Select(attrs={'class': 'form-select'}),
            'cantidad': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'subtotal': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'email_usuario': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Correo del usuario'}),
        }


# ---------- FORMSET: RELACIÓN 1 Pedido → N Detalles ----------
DetallePedidoFormSet = inlineformset_factory(
    Pedidos,
    Detalles_pedidos,
    form=DetallePedidosForm,
    extra=1,
    can_delete=True,
)


class PedidoInvitadoForm(forms.ModelForm):
    email_usuario = forms.EmailField(label="Tu correo electrónico")

    class Meta:
        model = Detalles_pedidos
        fields = ['producto', 'cantidad', 'email_usuario', 'pedido']
        widgets = {
            'pedido': forms.HiddenInput(),
        }
