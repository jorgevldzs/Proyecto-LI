from django import forms
from django.contrib.auth.models import User

from pages.models import Event
from .models import Member, HealthInfo, EmergencyContact, Vehicle, SEX_CHOICES, BLOOD_TYPE_CHOICES


class PersonalDataForm(forms.Form):
    first_name = forms.CharField(max_length=150, label="Nombre(s)")
    last_name = forms.CharField(max_length=150, label="Apellidos")
    sex = forms.ChoiceField(choices=SEX_CHOICES, label="Sexo")
    birth_date = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date"}),
        label="Fecha de nacimiento",
    )
    photo = forms.ImageField(required=False, label="Foto (opcional)")
    email = forms.EmailField(label="Correo electrónico")
    password1 = forms.CharField(widget=forms.PasswordInput, label="Contraseña")
    password2 = forms.CharField(widget=forms.PasswordInput, label="Confirmar contraseña")

    def clean_email(self):
        email = self.cleaned_data["email"]
        if len(email) > 150:
            raise forms.ValidationError("El correo es demasiado largo (máx. 150 caracteres).")
        if User.objects.filter(username=email).exists():
            raise forms.ValidationError("Ya existe una cuenta con este correo.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get("password1")
        p2 = cleaned_data.get("password2")
        if p1 and p2 and p1 != p2:
            self.add_error("password2", "Las contraseñas no coinciden.")
        return cleaned_data


class ContactForm(forms.Form):
    street = forms.CharField(max_length=200, label="Calle")
    house_number = forms.CharField(max_length=20, label="Número de casa")
    neighborhood = forms.CharField(max_length=200, label="Colonia")
    phone = forms.CharField(max_length=20, label="Número celular")


class HealthForm(forms.ModelForm):
    class Meta:
        model = HealthInfo
        exclude = ["member"]
        labels = {
            "blood_type": "Grupo sanguíneo",
            "has_allergies": "¿Tiene alergias?",
            "allergies_detail": "Especifique alergias",
            "has_physical_condition": "¿Tiene padecimiento físico?",
            "physical_condition_detail": "Especifique padecimiento",
            "under_medical_treatment": "¿Está bajo tratamiento médico?",
            "treatment_detail": "Especifique tratamiento",
            "takes_medication": "¿Toma algún medicamento?",
            "medication_detail": "Especifique medicamento(s)",
            "has_insurance": "¿Posee seguro médico?",
            "insurance_detail": "NSS o detalles del seguro",
        }
        widgets = {
            "blood_type": forms.Select(attrs={"class": "form-select"}),
            "allergies_detail": forms.Textarea(attrs={"rows": 2}),
            "physical_condition_detail": forms.Textarea(attrs={"rows": 2}),
            "treatment_detail": forms.Textarea(attrs={"rows": 2}),
            "medication_detail": forms.Textarea(attrs={"rows": 2}),
            "insurance_detail": forms.Textarea(attrs={"rows": 2}),
        }


class EmergencyContactForm(forms.ModelForm):
    class Meta:
        model = EmergencyContact
        exclude = ["member", "is_primary"]
        labels = {
            "first_name": "Nombre(s)",
            "last_name": "Apellidos",
            "relationship": "Parentesco",
            "phone": "Número celular",
        }

    def __init__(self, *args, required=True, **kwargs):
        super().__init__(*args, **kwargs)
        if not required:
            for field in self.fields.values():
                field.required = False


class VehicleForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        exclude = ["member"]
        labels = {
            "model": "Modelo",
            "plate": "Placa",
        }

    def __init__(self, *args, required=True, **kwargs):
        super().__init__(*args, **kwargs)
        if not required:
            for field in self.fields.values():
                field.required = False


class AcceptanceForm(forms.Form):
    liability_release = forms.BooleanField(
        label="Acepto la liberación de responsabilidad",
        required=True,
        error_messages={"required": "Debe aceptar la liberación de responsabilidad."},
    )
    data_treatment = forms.BooleanField(
        label="Acepto el tratamiento de datos personales",
        required=True,
        error_messages={"required": "Debe aceptar el tratamiento de datos personales."},
    )
    photo_permission = forms.BooleanField(
        label="Doy permiso para el uso de fotografías",
        required=True,
        error_messages={"required": "Debe otorgar permiso para fotografías."},
    )


class EditPhotoForm(forms.ModelForm):
    class Meta:
        model = Member
        fields = ["photo"]
        labels = {"photo": "Nueva foto de perfil"}


class EditContactForm(forms.ModelForm):
    email = forms.EmailField(label="Correo electrónico", required=False)
    first_name = forms.CharField(max_length=150, label="Nombre(s)")
    last_name = forms.CharField(max_length=150, label="Apellidos")

    class Meta:
        model = Member
        fields = ["street", "house_number", "neighborhood", "phone", "photo"]
        labels = {
            "street": "Calle",
            "house_number": "Número de casa",
            "neighborhood": "Colonia",
            "phone": "Número celular",
            "photo": "Foto de perfil",
        }


class EditEmergencyContactForm(forms.ModelForm):
    class Meta:
        model = EmergencyContact
        exclude = ["member", "is_primary"]
        labels = {
            "first_name": "Nombre(s)",
            "last_name": "Apellidos",
            "relationship": "Parentesco",
            "phone": "Número celular",
        }


class AddPhotoForm(forms.Form):
    image = forms.ImageField(label="Imagen")
    caption = forms.CharField(max_length=200, required=False, label="Descripción (opcional)")


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ["title", "description", "event_date", "location", "is_visible"]
        labels = {
            "title": "Título",
            "description": "Descripción",
            "event_date": "Fecha y hora",
            "location": "Lugar",
            "is_visible": "Visible en el sitio",
        }
        widgets = {
            "event_date": forms.DateTimeInput(attrs={"type": "datetime-local"}, format="%Y-%m-%dT%H:%M"),
            "description": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["event_date"].input_formats = ["%Y-%m-%dT%H:%M"]
        if self.instance and self.instance.pk and self.instance.event_date:
            self.initial["event_date"] = self.instance.event_date.strftime("%Y-%m-%dT%H:%M")
