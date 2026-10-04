from main.models import Peer


def profile(request):
    """Name, NPM and bio for base.html, so every page (403 included) has its footer."""
    return {
        "name": "Zhillan",
        "npm": "2506637174",
        "study_program": "S1 Ilmu Komputer KKI",
        "bio": "formally known as Zhillan Baniaksa",
    }


def guestbook(request):
    """The guestbook is the footer of every page, so its signatures ride along with every render."""
    return {"guest_list": Peer.objects.filter(show_in_peers=True).order_by("created_at")}
