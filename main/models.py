import re
import uuid
from django.db import models
from django.templatetags.static import static

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
        help_text="Path under static/, e.g. icons/peers/zayyan.png",
    )
    url = models.URLField(blank=True, null=True)
    order = models.PositiveBigIntegerField(default = 0)

    class Meta:
        ordering = ["order", "name"]

    def __str__(self):
        return self.name

    @property
    def icon_src(self):
        return media_src(self.icon)



class Project(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    year = models.CharField(max_length=16)
    role = models.CharField(max_length=120, blank=True)
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

    class Meta:
        ordering = ["order", "-year"]

    def __str__(self):
        return self.title

    @property
    def image_src(self):
        return media_src(self.image)

    
    @property
    def tech_list(self):
        return [tech.strip() for tech in self.tech_stack.split(",") if tech.strip()]

