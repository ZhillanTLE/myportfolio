from django.shortcuts import render
from main.models import Project, Peer
from main.forms import ProjectForm, PeerForm


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


PROFILE = {
    "name": "Zhillan",
    "npm": "2506637174",
    "study_program": "S1 Ilmu Komputer KKI",
    "bio": "formally known as Zhillan Baniaksa",
}


# Projects: data delivery

def _filtered_projects(request):
    title_query = request.GET.get("title", "").strip()
    projects = Project.objects.all()
    if title_query:
        projects = projects.filter(title__icontains=title_query)
    return projects


def get_projects_json(request):
    return HttpResponse(
        serializers.serialize("json", _filtered_projects(request)),
        content_type="application/json",
    )


def get_projects_xml(request):
    return HttpResponse(
        serializers.serialize("xml", _filtered_projects(request)),
        content_type="application/xml",
    )


def show_projects(request):
    # Read through the JSON endpoint instead of the ORM, then deserialize back into Project objects
    json_response = get_projects_json(request)
    deserialized = serializers.deserialize("json", json_response.content.decode("utf-8"))
    projects = [item.object for item in deserialized]

    context = {
        **PROFILE,
        "project_list": projects,
        "peer_list": Peer.objects.filter(show_in_peers=True),
        "title_query": request.GET.get("title", "").strip(),
    }
    return render(request, "projects.html", context)


# Projects: create / update / delete 

def _project_form_view(request, project=None):
    """Shared by create_project and update_project; project=None means create."""
    form = ProjectForm(request.POST or None, instance=project)

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
            form = ProjectForm(initial=initial, instance=project)
        elif form.is_valid():
            saved = form.save()
            if project is None:
                messages.success(request, f"{saved.title} added.")
            else:
                messages.success(request, f"{saved.title} updated.")
            return redirect("main:show_projects")

    context = {
        **PROFILE,
        "form": form,
        "project": project,
    }
    return render(request, "projects_form.html", context)


def create_project(request):
    return _project_form_view(request)


def update_project(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    return _project_form_view(request, project)


def delete_project(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if request.method == "POST":
        title = project.title
        project.delete()
        messages.success(request, f"{title} deleted.")
    return redirect("main:show_projects")


def create_peer(request):
    form = PeerForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        peer = form.save(commit=False)
        peer.show_in_peers = True
        peer.save()
        messages.success(request, "Peer berhasil ditambahkan!")
        return redirect("main:show_projects")

    context = {
        "name": "Zhillan",
                "npm": "2506637174",
                "study_program": "S1 Ilmu Komputer KKI",
                "bio": "formally known as Zhillan Baniaksa",
                "form": form,
    }
    return render(request, "peers_form.html", context)