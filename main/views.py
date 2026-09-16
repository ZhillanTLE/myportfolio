from django.shortcuts import render
from main.models import Project, Peer
from main.forms import ProjectForm


from django.contrib import messages
from django.core import serializers
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render


def show_main(request):
    context = {
        "name": "Zhillan",
        "npm": "2506637174",
        "study_program": "S1 Ilmu Komputer KKI",
        "bio": (
            "formally known as Zhillan Baniaksa"
        ),
    }
    return render(request, "index.html", context)


def show_projects(request):
    context = {
        "name": "Zhillan",
        "npm": "2506637174",
        "study_program": "S1 Ilmu Komputer KKI",
        "bio": "formally known as Zhillan Baniaksa",
        "project_list": Project.objects.prefetch_related("peers"),
    }

    return render(request, "projects.html", context)

def create_project(request):
    form = ProjectForm(request.POST or None)

    if request.method == "POST":
        if "add_peer" in request.POST:
            # "+" button: create the collaborator, keep the form filled, don't save yet
            name = request.POST.get("new_peer", "").strip()
            icon = request.POST.get("new_peer_icon", "").strip()
            selected = request.POST.getlist("peers")
            if name:
                peer = Peer.objects.filter(name__iexact=name).first()
                if peer is None:
                    peer = Peer.objects.create(
                        name=name,
                        icon=icon or "icons/peers/plusicon.jpeg",
                    )
                elif icon:
                    peer.icon = icon
                    peer.save()
                selected.append(str(peer.pk))
            initial = request.POST.dict()
            initial["peers"] = selected
            initial["new_peer"] = ""
            initial["new_peer_icon"] = ""
            form = ProjectForm(initial=initial)
        elif form.is_valid():
            form.save()
            messages.success(request, "Proyek baru berhasil ditambahkan!")
            return redirect("main:show_projects")

    context = {
        "name": "Zhillan",
        "npm": "2506637174",
        "study_program": "S1 Ilmu Komputer KKI",
        "bio": "formally known as Zhillan Baniaksa",
        "form": form,
    }
    return render(request, "projects_form.html", context)

