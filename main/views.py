from django.shortcuts import render

from main.models import Experience


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


def show_experience(request):
    context = {
        "name": "Zhillan",
        "experience_list": Experience.objects.all(),
    }
    return render(request, "experience.html", context)