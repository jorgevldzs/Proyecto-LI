from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction

from .models import Member, HealthInfo, EmergencyContact, Vehicle
from .forms import (
    PersonalDataForm, ContactForm, HealthForm, EmergencyContactForm, VehicleForm,
    AcceptanceForm, EditContactForm, EditEmergencyContactForm, AddPhotoForm,
)
from pages.models import MainPagePhoto


def _is_staff(user):
    return user.is_active and user.is_staff


def staff_required(view_func):
    from functools import wraps

    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(f"/login/?next={request.path}")
        if not _is_staff(request.user):
            messages.error(request, "No tienes permiso para acceder a esta sección.")
            return redirect("/")
        return view_func(request, *args, **kwargs)

    return wrapper


# ── Registration ──────────────────────────────────────────────────────────────

def register(request):
    if request.user.is_authenticated:
        return redirect("profile")

    if request.method == "POST":
        personal_form = PersonalDataForm(request.POST, request.FILES, prefix="p")
        contact_form = ContactForm(request.POST, prefix="c")
        health_form = HealthForm(request.POST, prefix="h")
        ec1_form = EmergencyContactForm(request.POST, prefix="ec1")
        ec2_form = EmergencyContactForm(request.POST, prefix="ec2", required=False)
        v1_form = VehicleForm(request.POST, prefix="v1")
        v2_form = VehicleForm(request.POST, prefix="v2", required=False)
        acceptance_form = AcceptanceForm(request.POST, prefix="acc")

        has_ec2 = bool(request.POST.get("ec2-first_name") or request.POST.get("ec2-last_name"))
        has_v2 = bool(request.POST.get("v2-model") or request.POST.get("v2-plate"))

        required_forms = [personal_form, contact_form, health_form, ec1_form, v1_form, acceptance_form]
        optional_forms_ok = True
        if has_ec2:
            required_forms.append(ec2_form)
        if has_v2:
            required_forms.append(v2_form)

        all_valid = all(f.is_valid() for f in required_forms)
        context_extra = {"show_ec2": has_ec2, "show_v2": has_v2}

        if all_valid:
            with transaction.atomic():
                pd = personal_form.cleaned_data
                cd = contact_form.cleaned_data
                acc = acceptance_form.cleaned_data

                user = User.objects.create_user(
                    username=pd["email"],
                    email=pd["email"],
                    password=pd["password1"],
                    first_name=pd["first_name"],
                    last_name=pd["last_name"],
                    is_active=False,
                )

                member = Member(
                    user=user,
                    sex=pd["sex"],
                    birth_date=pd["birth_date"],
                    street=cd["street"],
                    house_number=cd["house_number"],
                    neighborhood=cd["neighborhood"],
                    phone=cd["phone"],
                    status="pending",
                    liability_release=acc["liability_release"],
                    data_treatment=acc["data_treatment"],
                    photo_permission=acc["photo_permission"],
                )
                if pd.get("photo"):
                    member.photo = pd["photo"]
                member.save()

                hd = health_form.cleaned_data
                HealthInfo.objects.create(member=member, **hd)

                ec1 = ec1_form.save(commit=False)
                ec1.member = member
                ec1.is_primary = True
                ec1.save()

                if has_ec2 and ec2_form.is_valid():
                    ec2 = ec2_form.save(commit=False)
                    ec2.member = member
                    ec2.is_primary = False
                    ec2.save()

                v1 = v1_form.save(commit=False)
                v1.member = member
                v1.save()

                if has_v2 and v2_form.is_valid():
                    v2 = v2_form.save(commit=False)
                    v2.member = member
                    v2.save()

            return redirect("register_success")
    else:
        personal_form = PersonalDataForm(prefix="p")
        contact_form = ContactForm(prefix="c")
        health_form = HealthForm(prefix="h")
        ec1_form = EmergencyContactForm(prefix="ec1")
        ec2_form = EmergencyContactForm(prefix="ec2", required=False)
        v1_form = VehicleForm(prefix="v1")
        v2_form = VehicleForm(prefix="v2", required=False)
        acceptance_form = AcceptanceForm(prefix="acc")

    ctx = {
        "personal_form": personal_form,
        "contact_form": contact_form,
        "health_form": health_form,
        "ec1_form": ec1_form,
        "ec2_form": ec2_form,
        "v1_form": v1_form,
        "v2_form": v2_form,
        "acceptance_form": acceptance_form,
    }
    if request.method == "POST":
        ctx.update(context_extra)
    return render(request, "members/register.html", ctx)


def register_success(request):
    return render(request, "members/register_success.html")


# ── Member profile ─────────────────────────────────────────────────────────────

@login_required
def profile(request):
    member = get_object_or_404(Member, user=request.user)
    health = getattr(member, "health_info", None)
    contacts = member.emergency_contacts.all()
    vehicles = member.vehicles.all()
    return render(request, "members/profile.html", {
        "member": member,
        "health": health,
        "contacts": contacts,
        "vehicles": vehicles,
    })


@login_required
def edit_contact(request):
    member = get_object_or_404(Member, user=request.user)
    if request.method == "POST":
        form = EditContactForm(request.POST, request.FILES, instance=member, prefix="ec")
        if form.is_valid():
            form.save()
            user = request.user
            user.first_name = form.cleaned_data["first_name"]
            user.last_name = form.cleaned_data["last_name"]
            email = form.cleaned_data.get("email")
            if email:
                user.email = email
                user.username = email
            user.save()
            messages.success(request, "Datos de contacto actualizados.")
            return redirect("profile")
    else:
        form = EditContactForm(instance=member, prefix="ec", initial={
            "first_name": request.user.first_name,
            "last_name": request.user.last_name,
            "email": request.user.email,
        })
    return render(request, "members/edit_contact.html", {"form": form})


@login_required
def edit_health(request):
    member = get_object_or_404(Member, user=request.user)
    health, _ = HealthInfo.objects.get_or_create(member=member)
    if request.method == "POST":
        form = HealthForm(request.POST, instance=health, prefix="hf")
        if form.is_valid():
            form.save()
            messages.success(request, "Información de salud actualizada.")
            return redirect("profile")
    else:
        form = HealthForm(instance=health, prefix="hf")
    return render(request, "members/edit_health.html", {"form": form})


@login_required
def edit_emergency(request):
    member = get_object_or_404(Member, user=request.user)
    contacts = list(member.emergency_contacts.order_by("-is_primary"))
    ec1 = contacts[0] if contacts else None
    ec2 = contacts[1] if len(contacts) > 1 else None

    if request.method == "POST":
        form1 = EditEmergencyContactForm(request.POST, instance=ec1, prefix="ec1")
        form2 = EditEmergencyContactForm(request.POST, instance=ec2, prefix="ec2")
        has_ec2_data = bool(request.POST.get("ec2-first_name") or request.POST.get("ec2-last_name"))

        if form1.is_valid():
            c1 = form1.save(commit=False)
            c1.member = member
            c1.is_primary = True
            c1.save()
            if has_ec2_data and form2.is_valid():
                c2 = form2.save(commit=False)
                c2.member = member
                c2.is_primary = False
                c2.save()
            elif ec2 and not has_ec2_data:
                ec2.delete()
            messages.success(request, "Contactos de emergencia actualizados.")
            return redirect("profile")
    else:
        form1 = EditEmergencyContactForm(instance=ec1, prefix="ec1")
        form2 = EditEmergencyContactForm(instance=ec2, prefix="ec2")

    return render(request, "members/edit_emergency.html", {
        "form1": form1,
        "form2": form2,
        "has_ec2": ec2 is not None,
    })


@login_required
def edit_vehicles(request):
    member = get_object_or_404(Member, user=request.user)
    vehicles = list(member.vehicles.all())

    if request.method == "POST":
        action = request.POST.get("action")
        if action == "delete":
            vid = request.POST.get("vehicle_id")
            Vehicle.objects.filter(pk=vid, member=member).delete()
            messages.success(request, "Vehículo eliminado.")
            return redirect("edit_vehicles")

        form = VehicleForm(request.POST, prefix="vf")
        if form.is_valid():
            v = form.save(commit=False)
            v.member = member
            v.save()
            messages.success(request, "Vehículo agregado.")
            return redirect("edit_vehicles")
    else:
        form = VehicleForm(prefix="vf")

    return render(request, "members/edit_vehicles.html", {"form": form, "vehicles": vehicles})


# ── Member list & detail ───────────────────────────────────────────────────────

@login_required
def member_list(request):
    try:
        my_member = request.user.member
    except Member.DoesNotExist:
        messages.error(request, "No tienes un perfil de miembro.")
        return redirect("/")
    if my_member.status != "active":
        messages.warning(request, "Tu membresía aún no ha sido aprobada.")
        return redirect("profile")
    members = Member.objects.filter(status="active").exclude(user=request.user)
    return render(request, "members/member_list.html", {"members": members})


@login_required
def member_detail(request, pk):
    try:
        my_member = request.user.member
    except Member.DoesNotExist:
        return redirect("/")
    if my_member.status != "active":
        return redirect("profile")
    member = get_object_or_404(Member, pk=pk, status="active")
    health = getattr(member, "health_info", None)
    contacts = member.emergency_contacts.all()
    return render(request, "members/member_detail.html", {
        "member": member,
        "health": health,
        "contacts": contacts,
    })


# ── Admin panel ────────────────────────────────────────────────────────────────

@staff_required
def panel_dashboard(request):
    pending_count = Member.objects.filter(status="pending").count()
    active_count = Member.objects.filter(status="active").count()
    photos_count = MainPagePhoto.objects.count()
    return render(request, "members/panel_dashboard.html", {
        "pending_count": pending_count,
        "active_count": active_count,
        "photos_count": photos_count,
    })


@staff_required
def panel_requests(request):
    members = Member.objects.filter(status="pending").select_related("user")
    return render(request, "members/panel_requests.html", {"members": members})


@staff_required
def panel_member_detail(request, pk):
    member = get_object_or_404(Member, pk=pk)
    health = getattr(member, "health_info", None)
    contacts = member.emergency_contacts.all()
    vehicles = member.vehicles.all()
    return render(request, "members/panel_member_detail.html", {
        "member": member,
        "health": health,
        "contacts": contacts,
        "vehicles": vehicles,
    })


@staff_required
def panel_approve(request, pk):
    if request.method == "POST":
        member = get_object_or_404(Member, pk=pk)
        member.status = "active"
        member.user.is_active = True
        member.user.save()
        member.save()
        messages.success(request, f"{member.user.get_full_name()} ha sido aprobado.")
    return redirect("panel_requests")


@staff_required
def panel_reject(request, pk):
    if request.method == "POST":
        member = get_object_or_404(Member, pk=pk)
        member.status = "rejected"
        member.save()
        messages.success(request, f"{member.user.get_full_name()} ha sido rechazado.")
    return redirect("panel_requests")


@staff_required
def panel_all_members(request):
    members = Member.objects.select_related("user").all()
    return render(request, "members/panel_all_members.html", {"members": members})


@staff_required
def panel_photos(request):
    photos = MainPagePhoto.objects.all()
    form = AddPhotoForm()

    if request.method == "POST":
        action = request.POST.get("action")
        if action == "delete":
            pid = request.POST.get("photo_id")
            MainPagePhoto.objects.filter(pk=pid).delete()
            messages.success(request, "Foto eliminada.")
            return redirect("panel_photos")
        if action == "toggle":
            pid = request.POST.get("photo_id")
            photo = get_object_or_404(MainPagePhoto, pk=pid)
            photo.is_visible = not photo.is_visible
            photo.save()
            return redirect("panel_photos")
        form = AddPhotoForm(request.POST, request.FILES)
        if form.is_valid():
            MainPagePhoto.objects.create(
                image=form.cleaned_data["image"],
                caption=form.cleaned_data.get("caption", ""),
            )
            messages.success(request, "Foto agregada.")
            return redirect("panel_photos")

    return render(request, "members/panel_photos.html", {"photos": photos, "form": form})
