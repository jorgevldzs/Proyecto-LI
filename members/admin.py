from django.contrib import admin
from .models import Member, HealthInfo, EmergencyContact, Vehicle


class HealthInfoInline(admin.StackedInline):
    model = HealthInfo
    extra = 0


class EmergencyContactInline(admin.TabularInline):
    model = EmergencyContact
    extra = 0


class VehicleInline(admin.TabularInline):
    model = Vehicle
    extra = 0


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ("__str__", "phone", "status", "created_at")
    list_filter = ("status", "sex")
    search_fields = ("user__first_name", "user__last_name", "user__email", "phone")
    inlines = [HealthInfoInline, EmergencyContactInline, VehicleInline]
    actions = ["approve_members", "reject_members"]

    @admin.action(description="Aprobar miembros seleccionados")
    def approve_members(self, request, queryset):
        for member in queryset:
            member.status = "active"
            member.user.is_active = True
            member.user.save()
            member.save()

    @admin.action(description="Rechazar miembros seleccionados")
    def reject_members(self, request, queryset):
        queryset.update(status="rejected")
