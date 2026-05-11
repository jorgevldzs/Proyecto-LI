from django.urls import path
from . import views

urlpatterns = [
    path("registro/", views.register, name="register"),
    path("registro/exitoso/", views.register_success, name="register_success"),
    path("perfil/", views.profile, name="profile"),
    path("perfil/contacto/", views.edit_contact, name="edit_contact"),
    path("perfil/salud/", views.edit_health, name="edit_health"),
    path("perfil/emergencia/", views.edit_emergency, name="edit_emergency"),
    path("perfil/vehiculos/", views.edit_vehicles, name="edit_vehicles"),
    path("miembros/", views.member_list, name="member_list"),
    path("miembros/<int:pk>/", views.member_detail, name="member_detail"),
    path("panel/", views.panel_dashboard, name="panel_dashboard"),
    path("panel/solicitudes/", views.panel_requests, name="panel_requests"),
    path("panel/solicitudes/<int:pk>/", views.panel_member_detail, name="panel_member_detail"),
    path("panel/solicitudes/<int:pk>/aprobar/", views.panel_approve, name="panel_approve"),
    path("panel/solicitudes/<int:pk>/rechazar/", views.panel_reject, name="panel_reject"),
    path("panel/miembros/", views.panel_all_members, name="panel_all_members"),
    path("panel/fotos/", views.panel_photos, name="panel_photos"),
]
