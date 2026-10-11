def profile(request):
    """Name, NPM and bio for base.html, so every page (403 included) has its footer."""
    return {
        "name": "Zhillan",
        "npm": "2506637174",
        "study_program": "S1 Ilmu Komputer KKI",
        "bio": "formally known as Zhillan Baniaksa",
    }
