import base64
import datetime
import sys
from urllib.parse import quote

import requests
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from xhtml2pdf import pisa

from .forms import DatosPersonalesForm, FechaHoraForm
from .models import Propuesta

SESSION_KEY = "propuesta_datos"
NOTIFICACION_ELECCION_EMAIL = "samuelvalencia780@gmail.com"


def _rango_fechas():
    hoy = timezone.localdate()
    return hoy, settings.FECHA_LIMITE


def _whatsapp_link():
    """Link directo a mi chat de WhatsApp (funciona sin tenerme agregada)."""
    numero = "".join(c for c in settings.WHATSAPP_NUMERO if c.isdigit())
    if not numero:
        return None
    mensaje = quote("¡Hola! Vi la propuesta y quería escribirte ")
    return f"https://wa.me/{numero}?text={mensaje}"


def _enviar_correo_resend(
    destinatario, asunto, texto_plano, html=None, adjunto_nombre=None, adjunto_bytes=None, bcc=None
):
    """Envía un correo vía la API HTTP de Resend (Render bloquea SMTP saliente en el plan Free)."""
    if not settings.RESEND_API_KEY:
        mensaje = f"[correo consola] Para: {destinatario} | Asunto: {asunto}\n{texto_plano}"
        salida = sys.stdout.encoding or "utf-8"
        print(mensaje.encode(salida, errors="replace").decode(salida))
        return

    payload = {
        "from": settings.DEFAULT_FROM_EMAIL,
        "to": [destinatario],
        "subject": asunto,
        "text": texto_plano,
    }
    if html:
        payload["html"] = html
    if bcc:
        payload["bcc"] = [bcc]
    if adjunto_nombre and adjunto_bytes:
        payload["attachments"] = [{
            "filename": adjunto_nombre,
            "content": base64.b64encode(adjunto_bytes).decode("ascii"),
        }]

    respuesta = requests.post(
        "https://api.resend.com/emails",
        headers={
            "Authorization": f"Bearer {settings.RESEND_API_KEY}",
            "Content-Type": "application/json",
        },
        json=payload,
        timeout=10,
    )
    respuesta.raise_for_status()


@login_required
def inicio(request):
    """Pantalla 0: 'Nos podemos conocer?' con el botón No esquivo."""
    return render(request, "propuesta/inicio.html")


@login_required
def no_final(request):
    """A donde llega quien finalmente logra tocar 'No'."""
    return render(request, "propuesta/no_final.html")


@login_required
@csrf_exempt
@require_POST
def registrar_eleccion(request):
    """Avisa por correo (interno) si eligió 'Sí' o 'No' en la pantalla inicial."""
    eleccion = request.POST.get("eleccion")
    if eleccion not in ("si", "no"):
        return HttpResponseBadRequest()

    texto = "Sí" if eleccion == "si" else "No"
    try:
        _enviar_correo_resend(
            destinatario=NOTIFICACION_ELECCION_EMAIL,
            asunto=f'Propuesta de cita: eligió "{texto}"',
            texto_plano=f"{request.user.username} eligió: {texto}",
        )
    except Exception:
        pass
    return HttpResponse(status=204)


@login_required
def datos(request):
    """Pantalla 1: nombre, apellido, correo."""
    if request.method == "POST":
        form = DatosPersonalesForm(request.POST)
        if form.is_valid():
            request.session[SESSION_KEY] = {
                **request.session.get(SESSION_KEY, {}),
                **form.cleaned_data,
            }
            return redirect("propuesta:fecha")
    else:
        form = DatosPersonalesForm(initial=request.session.get(SESSION_KEY))

    return render(request, "propuesta/datos.html", {"form": form, "paso": 1})


@login_required
def fecha(request):
    """Pantalla 2: fecha (máx. N días) + hora (regla entre semana / fin de semana)."""
    if SESSION_KEY not in request.session:
        return redirect("propuesta:datos")

    hoy, hasta = _rango_fechas()

    if request.method == "POST":
        form = FechaHoraForm(request.POST)
        if form.is_valid():
            fecha_elegida = form.cleaned_data["fecha"]
            hora_elegida = form.cleaned_data["hora"]
            error = None

            if not (hoy <= fecha_elegida <= hasta):
                error = f"Elige una fecha entre {hoy.strftime('%d/%m')} y {hasta.strftime('%d/%m')}."
            elif fecha_elegida.weekday() < 5:  # lunes(0)-viernes(4)
                hora_min = datetime.datetime.strptime(
                    settings.HORA_MINIMA_ENTRE_SEMANA, "%H:%M"
                ).time()
                if hora_elegida < hora_min:
                    error = (
                        f"Entre semana solo hay disponibilidad desde las "
                        f"{hora_min.strftime('%H:%M')}."
                    )

            if not error:
                datos_sesion = request.session[SESSION_KEY]
                datos_sesion["fecha"] = fecha_elegida.isoformat()
                datos_sesion["hora"] = hora_elegida.isoformat()
                request.session[SESSION_KEY] = datos_sesion
                return redirect("propuesta:actividad")

            form.add_error(None, error)
    else:
        form = FechaHoraForm()

    return render(
        request,
        "propuesta/fecha.html",
        {
            "form": form,
            "paso": 2,
            "fecha_min": hoy.isoformat(),
            "fecha_max": hasta.isoformat(),
            "hora_minima_entre_semana": settings.HORA_MINIMA_ENTRE_SEMANA,
        },
    )


@login_required
def actividad(request):
    """Pantalla 3: elegir una de las 4 actividades."""
    if "fecha" not in request.session.get(SESSION_KEY, {}):
        return redirect("propuesta:fecha")

    if request.method == "POST":
        valor = request.POST.get("actividad")
        if valor in dict(Propuesta.ACTIVIDADES):
            datos_sesion = request.session[SESSION_KEY]
            datos_sesion["actividad"] = valor
            request.session[SESSION_KEY] = datos_sesion
            return redirect("propuesta:restaurante")

    return render(
        request,
        "propuesta/actividad.html",
        {"opciones": Propuesta.ACTIVIDADES, "paso": 3},
    )


@login_required
def restaurante(request):
    """Pantalla 4: elegir uno de los 4 restaurantes."""
    datos_sesion = request.session.get(SESSION_KEY, {})
    if "actividad" not in datos_sesion:
        return redirect("propuesta:actividad")

    if request.method == "POST":
        valor = request.POST.get("restaurante")
        if valor in dict(Propuesta.RESTAURANTES):
            datos_sesion["restaurante"] = valor
            request.session[SESSION_KEY] = datos_sesion
            return redirect("propuesta:confirmacion")

    return render(
        request,
        "propuesta/restaurante.html",
        {"opciones": Propuesta.RESTAURANTES, "paso": 4},
    )


def _generar_pdf_invitacion(propuesta_obj):
    html = render_to_string(
        "propuesta/pdf_invitacion.html",
        {"p": propuesta_obj, "whatsapp_link": _whatsapp_link()},
    )
    resultado = HttpResponse(content_type="application/pdf")
    pisa.CreatePDF(html, dest=resultado)
    return resultado.content


def _enviar_correo(propuesta_obj):
    contexto = {"p": propuesta_obj, "whatsapp_link": _whatsapp_link()}
    texto_plano = render_to_string("propuesta/correo_confirmacion.txt", contexto)
    html = render_to_string("propuesta/correo_confirmacion.html", contexto)

    pdf_bytes = None
    try:
        pdf_bytes = _generar_pdf_invitacion(propuesta_obj)
    except Exception:
        pass  # si el PDF falla, igual se envía el correo sin adjunto

    _enviar_correo_resend(
        destinatario=propuesta_obj.correo,
        asunto="Tenemos una cita 💌",
        texto_plano=texto_plano,
        html=html,
        adjunto_nombre="invitacion.pdf" if pdf_bytes else None,
        adjunto_bytes=pdf_bytes,
        bcc=settings.ADMIN_NOTIFICATION_EMAIL or NOTIFICACION_ELECCION_EMAIL,
    )


@login_required
def confirmacion(request):
    """Pantalla 5: guarda la propuesta, envía el correo y muestra el resumen."""
    datos_sesion = request.session.get(SESSION_KEY, {})
    if "restaurante" not in datos_sesion:
        return redirect("propuesta:restaurante")

    propuesta_obj = Propuesta.objects.filter(
        correo=datos_sesion["correo"],
        fecha=datos_sesion["fecha"],
        hora=datos_sesion["hora"],
    ).first()

    if propuesta_obj is None:
        propuesta_obj = Propuesta.objects.create(
            nombre=datos_sesion["nombre"],
            apellido=datos_sesion["apellido"],
            correo=datos_sesion["correo"],
            fecha=datetime.date.fromisoformat(datos_sesion["fecha"]),
            hora=datetime.time.fromisoformat(datos_sesion["hora"]),
            actividad=datos_sesion["actividad"],
            restaurante=datos_sesion["restaurante"],
        )
        try:
            _enviar_correo(propuesta_obj)
            propuesta_obj.correo_enviado = True
            propuesta_obj.save(update_fields=["correo_enviado"])
        except Exception:
            pass  # la pantalla igual muestra el resumen aunque el correo falle

    dias_restantes = (propuesta_obj.fecha - timezone.localdate()).days
    request.session.pop(SESSION_KEY, None)

    return render(
        request,
        "propuesta/confirmacion.html",
        {
            "p": propuesta_obj,
            "dias_restantes": dias_restantes,
            "paso": 5,
            "whatsapp_link": _whatsapp_link(),
        },
    )


@login_required
def descargar_invitacion(request, pk):
    """Permite volver a descargar el PDF desde la pantalla final."""
    propuesta_obj = Propuesta.objects.filter(pk=pk).first()
    if propuesta_obj is None:
        return redirect("propuesta:inicio")
    pdf_bytes = _generar_pdf_invitacion(propuesta_obj)
    respuesta = HttpResponse(pdf_bytes, content_type="application/pdf")
    respuesta["Content-Disposition"] = 'attachment; filename="invitacion.pdf"'
    return respuesta
