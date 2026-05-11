from django.contrib import admin
from .models import MainPagePhoto


@admin.register(MainPagePhoto)
class MainPagePhotoAdmin(admin.ModelAdmin):
    list_display = ("__str__", "is_visible", "uploaded_at")
    list_filter = ("is_visible",)
