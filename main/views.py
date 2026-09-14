from django.shortcuts import render

from main.models import Project


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