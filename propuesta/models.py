from django.conf import settings
from django.db import models


class Propuesta(models.Model):
    """Una propuesta de cita ya confirmada por la persona invitada."""

    ACTIVIDADES = [
        ("cine", "Cine"),
        ("gokart", "Go Kart"),
        ("boliche", "Boliche"),
        ("feria", "Feria / juegos mecánicos"),
    ]

    RESTAURANTES = [
        ("mcdonalds", "McDonald's"),
        ("pizza", "Pizza"),
        ("parrilla", "Parrilla / Asados"),
        ("sushi", "Sushi"),
    ]

    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="propuesta",
    )
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)

    fecha = models.DateField()
    hora = models.TimeField()

    actividad = models.CharField(max_length=20, choices=ACTIVIDADES)
    restaurante = models.CharField(max_length=20, choices=RESTAURANTES)

    respondio_si = models.BooleanField(default=True)
    correo_enviado = models.BooleanField(default=False)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Propuesta"
        verbose_name_plural = "Propuestas"
        ordering = ["-creado_en"]

    def __str__(self):
        return f"{self.nombre} {self.apellido} — {self.fecha} {self.hora}"

    @property
    def nombre_completo(self):
        return f"{self.nombre} {self.apellido}"
