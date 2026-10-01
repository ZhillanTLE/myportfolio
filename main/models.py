import re
import uuid
from django.db import models
from django.templatetags.static import static
from django.contrib.auth.models import User

HEADCOUNT = re.compile(r"^\+\s*(\d+)")
DRIVE_ID = re.compile(r"drive\.google\.com/(?:file/d/|open\?id=|uc\?(?:.*&)?id=)([\w-]+)")

def media_src(value):
    """Turn a stored path or URL into something an <img src> can actually load."""
    match = DRIVE_ID.search(value)
    if match:
        # Drive share link serves a web page, not the image; the thumbnail endpoint serves the file
        return f"https://drive.google.com/thumbnail?id={match.group(1)}&sz=w1000"
    if value.startswith("http"):
        return value
    return static(value)


class Experience(models.Model):
    EXPERIENCE_CHOICES = [
        ('internship', 'Internship'),
        ('research', 'Research'),
        ('volunteer', 'Volunteer'),
        ('part-time', 'Part-Time'),
        ('full-time', 'Full-Time'),
        ('freelance', 'Freelance'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=EXPERIENCE_CHOICES, default='full-time')
    thumbnail = models.URLField(blank=True, null=True)
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(blank=True, null=True)
    def __str__(self):
        return self.title
    
    @property
    def is_ongoing(self):
        return self.ended_at is None

class Peer(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    icon = models.CharField(
        max_length=255,
        blank=True,
        help_text="Path under static/, e.g. icons/peers/zayyan.png",
    )
    url = models.URLField(blank=True, null=True)
    order = models.PositiveBigIntegerField(default = 0)
    created_at = models.DateTimeField(auto_now_add=True)
    message = models.TextField(blank=True, default="")
    show_in_peers = models.BooleanField(default=False)

    class Meta:
        ordering = ["order", "name"]

    def __str__(self):
        return self.name

    @property
    def icon_src(self):
        return media_src(self.icon) if self.icon else ""

    @property
    def headcount(self):
        """A placeholder peer like "+34 Others" stands for 34 people, everyone else for one."""
        match = HEADCOUNT.match(self.name)
        return int(match.group(1)) if match else 1

    @property
    def is_placeholder(self):
        return bool(HEADCOUNT.match(self.name))



class Project(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    year = models.CharField(max_length=16)
    role = models.CharField(max_length=120, blank=True)
    context = models.CharField(
        max_length=160,
        blank=True,
        help_text="Where it was built or how it did, e.g. Ranked 6 of 250+ at AIC COMPFEST 18",
    )
    description = models.TextField()
    image = models.CharField(
        max_length=255,
        blank=True,
        help_text="Path under static/, e.g. img/projects/tinta.png",
    )
    tech_stack = models.CharField(
        max_length=255,
        help_text="Comma-separated, e.g. Django, Postgres, React",
    )
    peers = models.ManyToManyField(Peer, blank=True, related_name="projects")
    repo_url = models.URLField(blank=True, null=True)
    live_url = models.URLField(blank=True, null=True)
    order = models.PositiveIntegerField(default=0)
    starred_by = models.ManyToManyField(User, related_name="starred_project", blank=True)

    class Meta:
        ordering = ["order", "-year"]

    def __str__(self):
        return self.title

    @property
    def image_src(self):
        return media_src(self.image)

    
    @property
    def team_label(self):
        """3 people, or 4 + 34 others when a placeholder peer stands in for a crowd."""
        peers = list(self.peers.all())
        named = sum(1 for peer in peers if not peer.is_placeholder)
        others = sum(peer.headcount for peer in peers if peer.is_placeholder)
        label = f"{named} {'person' if named == 1 else 'people'}"
        return f"{named} + {others} others" if others else label

    @property
    def tech_list(self):
        return [tech.strip() for tech in self.tech_stack.split(",") if tech.strip()]

