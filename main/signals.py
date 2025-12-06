from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Clientes

@receiver(post_save, sender=User)
def create_cliente(sender, instance, created, **kwargs):
    if created:
        Clientes.objects.create(
            user=instance,
            nombre=instance.first_name or "",
            apellido=instance.last_name or "",
            email=instance.email
        )
