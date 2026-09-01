from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit
from django import forms
from django.contrib.auth.forms import AuthenticationForm


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs.update({
            "placeholder": "Usuario",
            "autocomplete": "username",
            "autofocus": True,
        })
        self.fields["password"].widget.attrs.update({
            "placeholder": "Contraseña",
            "autocomplete": "current-password",
        })
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout("username", "password")


class DatosPersonalesForm(forms.Form):
    nombre = forms.CharField(
        label="Nombre",
        max_length=100,
        initial="Emily",
        disabled=True,
    )
    apellido = forms.CharField(
        label="Apellido",
        max_length=100,
        initial="Macias",
        disabled=True,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Row(
                Column("nombre", css_class="col-md-6"),
                Column("apellido", css_class="col-md-6"),
            ),
        )


class FechaHoraForm(forms.Form):
    fecha = forms.DateField(
        label="Fecha",
        widget=forms.DateInput(attrs={"type": "date"}),
    )
    hora = forms.TimeField(
        label="Hora",
        widget=forms.TimeInput(attrs={"type": "time"}),
    )
