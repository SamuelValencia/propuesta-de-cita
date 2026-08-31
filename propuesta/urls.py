from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

from . import views
from .forms import LoginForm

app_name = "propuesta"

urlpatterns = [
    path(
        "login/",
        LoginView.as_view(
            template_name="propuesta/login.html",
            authentication_form=LoginForm,
            redirect_authenticated_user=True,
        ),
        name="login",
    ),
    path("logout/", LogoutView.as_view(next_page="propuesta:login"), name="logout"),
    path("", views.inicio, name="inicio"),
    path("no/", views.no_final, name="no_final"),
    path("eleccion/", views.registrar_eleccion, name="registrar_eleccion"),
    path("datos/", views.datos, name="datos"),
    path("fecha/", views.fecha, name="fecha"),
    path("actividad/", views.actividad, name="actividad"),
    path("restaurante/", views.restaurante, name="restaurante"),
    path("confirmacion/", views.confirmacion, name="confirmacion"),
    path("invitacion/<int:pk>/", views.descargar_invitacion, name="descargar_invitacion"),
]
