from django.shortcuts import render
from pages.models import MainPagePhoto


def home(request):
    photos = MainPagePhoto.objects.filter(is_visible=True)
    return render(request, "pages/home.html", {"photos": photos})
