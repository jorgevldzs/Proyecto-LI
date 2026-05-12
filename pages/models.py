from django.db import models


class Event(models.Model):
    title = models.CharField(max_length=200, verbose_name="Título")
    description = models.TextField(blank=True, verbose_name="Descripción")
    event_date = models.DateTimeField(verbose_name="Fecha y hora")
    location = models.CharField(max_length=300, blank=True, verbose_name="Lugar")
    is_visible = models.BooleanField(default=True, verbose_name="Visible")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Evento"
        verbose_name_plural = "Eventos"
        ordering = ["event_date"]

    def __str__(self):
        return self.title


class MainPagePhoto(models.Model):
    image = models.ImageField(upload_to="main_photos/")
    caption = models.CharField(max_length=200, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    is_visible = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Foto de Página Principal"
        verbose_name_plural = "Fotos de Página Principal"
        ordering = ["-uploaded_at"]

    def __str__(self):
        return self.caption or f"Foto #{self.pk}"
