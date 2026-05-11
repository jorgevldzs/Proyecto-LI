from django.db import models


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
