from django.contrib import admin
from .models import Event, MainPagePhoto


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("title", "event_date", "location", "is_visible")
    list_filter = ("is_visible",)
    ordering = ("event_date",)


@admin.register(MainPagePhoto)
class MainPagePhotoAdmin(admin.ModelAdmin):
    list_display = ("__str__", "is_visible", "uploaded_at")
    list_filter = ("is_visible",)
