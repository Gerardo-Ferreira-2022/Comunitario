from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now
from datetime import datetime
from geopy.geocoders import Nominatim
from django.db.models.signals import pre_save
from django.dispatch import receiver

# Create your models here.

class Task(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rut = models.CharField(max_length=20, verbose_name="RUT")
    email = models.EmailField(verbose_name="Correo electrónico")
    descripcion = models.TextField(verbose_name="Descripción")
    latitud = models.DecimalField(max_digits=9, decimal_places=6, verbose_name="Latitud")
    longitud = models.DecimalField(max_digits=9, decimal_places=6, verbose_name="Longitud")
    fecha = models.DateField(default=now, verbose_name="Fecha")
    hora = models.TimeField(default=now, verbose_name="Hora")
    dias_transcurridos = models.IntegerField(default=0, verbose_name="Días transcurridos")
    estado = models.CharField(max_length=50,
        choices=[
            ('Pendiente', 'Pendiente'),
            ('En Proceso', 'En Proceso'),
            ('Completada', 'Completada'),
        ],
        default='Pendiente',
        verbose_name="Estado",
    )

    def __str__(self):
        return f"Task: {self.user} - {self.estado}"
    


class FormModel(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.TextField()
    latitude = models.DecimalField(max_digits=10, decimal_places=5)  # Redondeado a 5 decimales
    longitude = models.DecimalField(max_digits=10, decimal_places=5)  # Redondeado a 5 decimales
    address = models.CharField(max_length=255, blank=True, null=True)  # Nueva columna para la dirección
    created_at = models.DateTimeField(auto_now_add=True)  # Fecha y hora de creación

    def __str__(self):
        return f"{self.user.username} - {self.comment}"

    def get_address(self):
        # Usar Geopy para obtener la dirección a partir de la latitud y longitud
        geolocator = Nominatim(user_agent="mi_aplicacion")
        location = geolocator.reverse((self.latitude, self.longitude))
        if location:
            return location.address
        return "Dirección no disponible"

# Función para asignar la dirección antes de guardar el objeto
@receiver(pre_save, sender=FormModel)
def update_address(sender, instance, **kwargs):
    if instance.latitude and instance.longitude:
        instance.address = instance.get_address()


