# Propuesta de Cita 💌

Sitio web construido con **Django** que guía a la persona invitada por 5 pantallas
(pregunta inicial, datos, fecha/hora, actividad, restaurante) y termina enviándole
un correo de confirmación con una invitación en PDF adjunta.

## Qué tecnologías se usaron y por qué

De la lista de tecnologías de tu otro proyecto, usé lo que realmente aportaba a
este flujo puntual:

| Tecnología | Para qué se usó aquí |
|---|---|
| Django 4.2 | Framework principal (vistas, formularios, sesiones, admin) |
| django-crispy-forms + crispy-bootstrap5 | Formulario de datos personales bien formateado |
| Bootstrap 5 + Font Awesome | Grid responsive e íconos de las tarjetas |
| WhiteNoise | Servir CSS/JS en producción sin depender de un servidor aparte |
| python-decouple | Variables de entorno (.env) para no hardcodear claves |
| dj-database-url + psycopg2 | Conectar a Postgres/Supabase en producción, SQLite en local |
| xhtml2pdf + ReportLab | Generar el PDF de invitación que se adjunta al correo |
| Gunicorn | Servidor de producción para Render |
| Django Auth (admin) | Panel donde tú revisas las respuestas guardadas, en `/admin/` |

**Dejé fuera** (porque no aportaban a esta funcionalidad puntual): Django REST
Framework, django-filter, django-guardian, django-cors-headers, Twilio,
SendGrid, PyJWT, cryptography/pyHanko, Select2/DataTables/jQuery, openpyxl y
python-docx. Si más adelante quieres, por ejemplo, un recordatorio por WhatsApp
el día antes de la cita, ahí sí tendría sentido sumar Twilio.

## Instalación local

```bash
python3 -m venv venv
source venv/bin/activate        # En Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env            # y edita los valores que necesites
python manage.py migrate
python manage.py createsuperuser   # para poder entrar a /admin/
python manage.py runserver
```

Abre `http://127.0.0.1:8000/`.

Si no configuras `RESEND_API_KEY` en `.env`, los correos no se envían de
verdad: se imprimen en la consola donde corre `runserver`, para que puedas
probar el flujo completo sin necesidad de credenciales reales.

## Configurar el envío real de correos (Resend)

Los correos se envían por la **API HTTP** de Resend (no por SMTP), porque
Render bloquea el tráfico saliente a puertos SMTP en su plan gratuito.

1. Crea una cuenta gratis en [resend.com](https://resend.com).
2. En el panel, genera una **API Key** (empieza con `re_...`).
3. En tu `.env`, pon esa key en `RESEND_API_KEY`.
4. Por defecto los correos salen desde `onboarding@resend.dev` (dominio de
   pruebas de Resend, no requiere configuración extra). Si quieres un
   remitente propio, verifica un dominio que controles en Resend y cambia
   `DEFAULT_FROM_EMAIL` por una dirección de ese dominio — Resend no permite
   usar direcciones de dominios que no verificaste (como `gmail.com`), por
   temas de seguridad anti-spam.

## Personalizar el contenido

- **Actividades y restaurantes**: están definidos en `propuesta/models.py`
  (`ACTIVIDADES` y `RESTAURANTES`) y sus íconos en
  `templates/propuesta/actividad.html` / `restaurante.html`. Si cambias las
  opciones, corre de nuevo `python manage.py makemigrations && python manage.py migrate`.
- **Textos e imágenes**: cada pantalla es un archivo en `templates/propuesta/`.
  Las "imágenes" de cada opción son íconos de Font Awesome dentro de un
  círculo; si prefieres fotos reales, reemplaza el `<i class="fa-solid ...">`
  por un `<img src="...">` centrado.
- **Reglas de fecha**: `FECHA_LIMITE` y `HORA_MINIMA_ENTRE_SEMANA` se
  configuran desde `.env`, sin tocar código.
- **Colores y tipografía**: todo vive en `static/css/estilo.css` (variables al
  inicio del archivo).

## Ver las respuestas guardadas

Entra a `/admin/` con el usuario que creaste con `createsuperuser`. Ahí verás
cada propuesta confirmada: nombre, correo, fecha, hora, actividad,
restaurante y si el correo se envió correctamente.

## Desplegar en Render + Supabase

1. **Supabase**: crea un proyecto en [supabase.com](https://supabase.com) →
   ve a *Project Settings → Database* → copia la "Connection string" (modo
   *URI*). Esa es tu `DATABASE_URL`.
2. **Render**: crea un *Web Service* nuevo apuntando a tu repositorio.
   - Build command: `./build.sh`
   - Start command: `gunicorn citaproject.wsgi`
   - Agrega todas las variables de `.env.example` en la sección
     *Environment* de Render (con `DEBUG=False` y tu `DATABASE_URL` real de
     Supabase).
3. Cuando el deploy termine, crea el superusuario de producción con la
   consola de Render:
   ```bash
   python manage.py createsuperuser
   ```

## Estructura del proyecto

```
citaproject/        # configuración del proyecto (settings, urls)
propuesta/           # la app: modelos, formularios, vistas, urls, admin
templates/propuesta/ # las 8 pantallas HTML
static/css/          # estilos
static/js/           # (vacío por ahora; el JS de cada pantalla vive inline)
requirements.txt
.env.example
Procfile
build.sh
```
