from django.contrib import admin

from .models import Propuesta


@admin.register(Propuesta)
class PropuestaAdmin(admin.ModelAdmin):
    list_display = (
        "nombre_completo",
        "correo",
        "fecha",
        "hora",
        "actividad",
        "restaurante",
        "correo_enviado",
        "creado_en",
    )
    list_filter = ("actividad", "restaurante", "correo_enviado", "fecha")
    search_fields = ("nombre", "apellido", "correo")
    readonly_fields = ("creado_en",)
