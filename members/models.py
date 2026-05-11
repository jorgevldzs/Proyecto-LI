from django.db import models
from django.contrib.auth.models import User

BLOOD_TYPE_CHOICES = [
    ("A+", "A+"), ("A-", "A-"),
    ("B+", "B+"), ("B-", "B-"),
    ("AB+", "AB+"), ("AB-", "AB-"),
    ("O+", "O+"), ("O-", "O-"),
]

SEX_CHOICES = [
    ("M", "Masculino"),
    ("F", "Femenino"),
    ("O", "Otro"),
]

STATUS_CHOICES = [
    ("pending", "Pendiente"),
    ("active", "Activo"),
    ("rejected", "Rechazado"),
]


class Member(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="member")
    sex = models.CharField(max_length=1, choices=SEX_CHOICES)
    birth_date = models.DateField()
    photo = models.ImageField(upload_to="members/photos/", blank=True, null=True)
    street = models.CharField(max_length=200)
    house_number = models.CharField(max_length=20)
    neighborhood = models.CharField(max_length=200)
    phone = models.CharField(max_length=20)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)
    liability_release = models.BooleanField(default=False)
    data_treatment = models.BooleanField(default=False)
    photo_permission = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Miembro"
        verbose_name_plural = "Miembros"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.get_status_display()})"


class HealthInfo(models.Model):
    member = models.OneToOneField(Member, on_delete=models.CASCADE, related_name="health_info")
    blood_type = models.CharField(max_length=3, choices=BLOOD_TYPE_CHOICES)
    has_allergies = models.BooleanField(default=False)
    allergies_detail = models.TextField(blank=True)
    has_physical_condition = models.BooleanField(default=False)
    physical_condition_detail = models.TextField(blank=True)
    under_medical_treatment = models.BooleanField(default=False)
    treatment_detail = models.TextField(blank=True)
    takes_medication = models.BooleanField(default=False)
    medication_detail = models.TextField(blank=True)
    has_insurance = models.BooleanField(default=False)
    insurance_detail = models.TextField(blank=True)

    class Meta:
        verbose_name = "Información de Salud"
        verbose_name_plural = "Información de Salud"

    def __str__(self):
        return f"Salud — {self.member.user.get_full_name()}"


class EmergencyContact(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name="emergency_contacts")
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    relationship = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    is_primary = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Contacto de Emergencia"
        verbose_name_plural = "Contactos de Emergencia"
        ordering = ["-is_primary"]

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({'Primario' if self.is_primary else 'Secundario'})"


class Vehicle(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name="vehicles")
    model = models.CharField(max_length=200, verbose_name="Modelo")
    plate = models.CharField(max_length=20, verbose_name="Placa")

    class Meta:
        verbose_name = "Vehículo"
        verbose_name_plural = "Vehículos"

    def __str__(self):
        return f"{self.model} — {self.plate}"
