from django.shortcuts import render
from main.models import Project, Peer
from main.forms import ProjectForm, PeerForm, TeammateForm, find_or_create_collaborator


from django.contrib import messages
from django.core import serializers
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import login, logout
import datetime
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied

from django.urls import reverse
from django.views.decorators.http import require_POST
from django.utils.http import url_has_allowed_host_and_scheme
from django.utils.dateformat import format as format_date


def show_main(request):
    last_login = request.COOKIES.get('last_login', 'No active login session / Cookie not found.')
    context = {
        "name": "Zhillan",
        "npm": "2506637174",
        "study_program": "S1 Ilmu Komputer KKI",
        "bio": "formally known as Zhillan Baniaksa",
        "last_login" : last_login,

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


# starred_by is left out on purpose: serialized, it lists every starrer's username
PUBLIC_FIELDS = ("title", "year", "role", "context", "description", "image",
                 "tech_stack", "repo_url", "live_url", "order", "peers")

def get_projects_json(request):
    title_query = request.GET.get("title", "").strip()
    projects = Project.objects.prefetch_related('starred_by', 'peers').all()

    if title_query:
        projects = projects.filter(title__icontains=title_query)

    # Manually build the JSON data so we can add the Star logic
    data = []
    for project in projects:
        starred_users = project.starred_by.all()
        is_starred = request.user in starred_users if request.user.is_authenticated else False
        starred_by_names = ", ".join([u.username for u in starred_users])

        data.append({
            "pk": str(project.id),
            "fields": {
                "title": project.title,
                "year": project.year,
                "role": project.role,
                "context": project.context,
                "team_label": project.team_label,
                "description": project.description,
                "tech_stack": project.tech_stack,
                "tech_list": project.tech_list,
                "live_url": project.live_url,
                "repo_url": project.repo_url,
                "project_image_url": project.image_src if project.image else "",
                "peers": [
                    {"pk": str(peer.pk), "name": peer.name, "icon_url": peer.icon_src}
                    for peer in project.peers.all()
                ],
                "star_count": len(starred_users),
                "is_starred": is_starred,
                "starred_by_names": starred_by_names,
            }
        })

    return JsonResponse(data, safe=False)


def get_projects_xml(request):
    return HttpResponse(
        serializers.serialize("xml", _filtered_projects(request), fields=PUBLIC_FIELDS),
        content_type="application/xml",
    )


def show_projects(request):
    # Projects are fetched by the page itself from get_projects_json (AJAX)
    context = {
        **PROFILE,
        "title_query": request.GET.get("title", "").strip(),
    }
    if request.user.has_perm("main.add_project"):
        context["form"] = ProjectForm()
    if request.user.has_perm("main.change_project"):
        context["teammate_form"] = TeammateForm()
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
                peer = find_or_create_collaborator(name, icon)
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

@login_required(login_url="/login/")
def update_project(request, project_id):
    if not request.user.has_perm("main.change_project"):
        raise PermissionDenied("Editing projects is for editors.")
    project = get_object_or_404(Project, pk=project_id)
    return _project_form_view(request, project)

# Create and Update projects
@login_required(login_url="/login/")
def create_project(request):
    if not request.user.has_perm("main.add_project"):
        raise PermissionDenied("Adding projects is for editors.")
    return _project_form_view(request)

@login_required(login_url="/login/")
def delete_project(request, project_id):
    if not request.user.has_perm("main.delete_project"):
        raise PermissionDenied("Only the admin can delete projects.")
    project = get_object_or_404(Project, pk=project_id)
    if request.method == "POST":
        title = project.title
        project.delete()
        messages.success(request, f"{title} deleted.")
    return redirect("main:show_projects")


def _wants_json(request):
    return request.headers.get("x-requested-with") == "XMLHttpRequest"


def create_peer(request):
    """Signs the guestbook. The footer row on every page posts here with fetch; this page is the fallback."""
    form = PeerForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        peer = form.save(commit=False)
        peer.show_in_peers = True
        peer.save()
        if _wants_json(request):
            return JsonResponse({
                "name": peer.name,
                "message": peer.message,
                "icon_url": peer.icon_src,
                "signed": format_date(peer.created_at, "j M Y"),
            }, status=201)
        messages.success(request, "Signed. Thanks for stopping by!")
        back = request.META.get("HTTP_REFERER", "")
        if not url_has_allowed_host_and_scheme(back, allowed_hosts={request.get_host()}):
            back = reverse("main:show_main")
        return redirect(back.split("#")[0] + "#guestbook")

    if request.method == "POST" and _wants_json(request):
        return JsonResponse({"errors": form.errors.get_json_data()}, status=400)

    context = {
        "name": "Zhillan",
                "npm": "2506637174",
                "study_program": "S1 Ilmu Komputer KKI",
                "bio": "formally known as Zhillan Baniaksa",
                "form": form,
    }
    return render(request, "peers_form.html", context)

# Authorization and Authentication
def register(request): 
    form = UserCreationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Account created successfully. Please log in.")
        return redirect("main:login")

    context = {
        "form" : form,
    }
    return render(request, "register.html", context)

def login_user(request):
    form = AuthenticationForm(request, data=request.POST or None)
    next_url = request.POST.get("next") or request.GET.get("next", "")
    
    if request.method == "POST" and form.is_valid():
        user = form.get_user()
        login(request, user)
        if not url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
            next_url = "main:show_main"
        response = redirect(next_url)
        response.set_cookie('last_login', datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        return response

    context = {
        "form" : form,
        "next" : next_url,
    }
    return render(request, "login.html", context)

def logout_user(request):
    logout(request)
    response = redirect("main:show_main")
    response.delete_cookie("last_login")
    return response

@login_required(login_url="/login/")
@require_POST
def toggle_star(request, project_id):
    project = get_object_or_404(Project, pk = project_id)
    if request.method == "POST":
        if request.user in project.starred_by.all():
            project.starred_by.remove(request.user)
        else:
            project.starred_by.add(request.user)

    # Back to the same card instead of the first one
    return redirect(reverse("main:show_projects") + f"#project-{project.id}")

# Create Project AJAX
@require_POST
def create_project_ajax(request):
    if not request.user.has_perm("main.add_project"):
        return JsonResponse(
            {"message": "Only the portfolio owner can add projects."},
            status=403,
        )

    form = ProjectForm(request.POST)
    if form.is_valid():
        project = form.save()
        return JsonResponse(
            {"message": "Project added successfully.", "pk": str(project.id)},
            status=201,
        )

    return JsonResponse({"errors": form.errors.get_json_data()}, status=400)


# Teams: add someone to one or more project teams
@require_POST
def add_teammate(request):
    if not request.user.has_perm("main.change_project"):
        return JsonResponse({"message": "Only editors can change teams."}, status=403)

    form = TeammateForm(request.POST)
    if form.is_valid():
        peer = form.save()
        return JsonResponse({"message": f"{peer.name} added.", "pk": str(peer.pk)}, status=201)

    return JsonResponse({"errors": form.errors.get_json_data()}, status=400)
