from django.forms import (
    CharField,
    CheckboxSelectMultiple,
    Form,
    ModelForm,
    ModelMultipleChoiceField,
    Textarea,
    TextInput,
    URLField,
    URLInput,
)
from main.models import Project, Peer
from django.core.exceptions import ValidationError
from django.utils.html import strip_tags


def collaborators():
    """Collaborators and guestbook signatures share Peer; a signature always carries a message."""
    return Peer.objects.filter(show_in_peers=False, message="")


def find_or_create_collaborator(name, icon=""):
    peer = collaborators().filter(name__iexact=name).first()
    if peer is None:
        return Peer.objects.create(name=name, icon=icon)
    if icon:
        peer.icon = icon
        peer.save(update_fields=["icon"])
    return peer


class ProjectForm(ModelForm):
    # Extra inputs for the "+" button; not model fields
    new_peer = CharField(
        required=False,
        widget=TextInput(attrs={"placeholder": "New collaborator"}),
    )
    new_peer_icon = URLField(
        required=False,
        widget=URLInput(attrs={"placeholder": "Photo drive URL"}),
    )


    class Meta:
        model = Project
        fields = [
            "title",
            "year",
            "image",
            "role",
            "tech_stack",
            "context",
            "description",
            "peers",
            "repo_url",
            "live_url",
        ]

        labels = {
            "title": "Project Name",
            "year": "Year",
            "image": "Image",
            "role": "Role",
            "tech_stack": "Stack",
            "context": "Context",
            "description": "Description",
            "peers": "Built by",
            "repo_url": "Repository Link",
            "live_url": "Live URL",
        }

        widgets = {
            "title": TextInput(attrs={"placeholder": "What project??", "maxlength": 255}),
            "year": TextInput(attrs={"placeholder": "202x?", "maxlength": 16}),
            "image": TextInput(attrs={"placeholder": "https://drive.google.com/.."}),
            "role": TextInput(attrs={"placeholder": "Gak UIUX lagi kan?", "maxlength": 120}),
            "tech_stack": TextInput(attrs={"placeholder": "Next.js, Django, .."}),
            "context": TextInput(attrs={"placeholder": "Ranked 6 of 250+ at ..", "maxlength": 160}),
            "description": Textarea(attrs={"placeholder": "First sentence is the headline. Yapping after that.", "rows": 5}),
            "peers": CheckboxSelectMultiple(),
            "repo_url": URLInput(attrs={"placeholder": "https://github.com/..."}),
            "live_url": URLInput(attrs={"placeholder": "https://.."}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name in ("role", "image", "context"):
            self.fields[name].required = True
        self.fields["tech_stack"].required = False
        # "Built by" is satisfied by a ticked chip or a new collaborator typed in, checked in clean()
        self.fields["peers"].required = False
        self.fields["peers"].queryset = collaborators()

    def clean_title(self):
        title = strip_tags(self.cleaned_data["title"]).strip()
        if not title:
            raise ValidationError("Project name can't contain only HTML tags.")
        return title

    def clean_role(self):
        return strip_tags(self.cleaned_data["role"]).strip()

    def clean_context(self):
        return strip_tags(self.cleaned_data["context"]).strip()

    def clean_tech_stack(self):
        return strip_tags(self.cleaned_data["tech_stack"]).strip()

    def clean_description(self):
        return strip_tags(self.cleaned_data["description"]).strip()

    def clean_new_peer(self):
        return strip_tags(self.cleaned_data["new_peer"]).strip()

    def clean(self):
        cleaned = super().clean()
        if not cleaned.get("peers") and not cleaned.get("new_peer"):
            self.add_error("peers", "Pick at least one builder, or add a new one.")
        return cleaned

    def save(self, commit=True):
        project = super().save(commit=commit)
        name = self.cleaned_data.get("new_peer")
        if commit and name:
            peer = find_or_create_collaborator(name, self.cleaned_data.get("new_peer_icon", ""))
            project.peers.add(peer)
        return project


class TeammateForm(Form):
    """Adds a person to one or more project teams without opening the whole project form."""
    name = CharField(
        max_length=100,
        widget=TextInput(attrs={"placeholder": "Name", "maxlength": 100}),
    )
    icon = URLField(
        required=False,
        label="Photo",
        widget=URLInput(attrs={"placeholder": "Photo drive URL (optional)"}),
    )
    projects = ModelMultipleChoiceField(
        queryset=Project.objects.all(),
        widget=CheckboxSelectMultiple(),
        label="Teams",
        error_messages={"required": "Pick at least one team."},
    )

    def clean_name(self):
        name = strip_tags(self.cleaned_data["name"]).strip()
        if not name:
            raise ValidationError("Name can't contain only HTML tags.")
        return name

    def save(self):
        peer = find_or_create_collaborator(self.cleaned_data["name"], self.cleaned_data["icon"])
        for project in self.cleaned_data["projects"]:
            project.peers.add(peer)
        return peer


class PeerForm(ModelForm):
    class Meta:
        model = Peer
        fields = ["name", "icon", "message"]

        labels = {
            "name" : "Name",
            "icon" : "Profile Picture",
            "message" : "Message",
        }

        widgets = {
            "name" : TextInput(attrs={"placeholder":"Your Name", "maxlength":100}),
            "icon" : TextInput(attrs={"placeholder":"https:drive.google.com/...", "maxlength":256}),
            "message" : TextInput(attrs={"placeholder": "Message", "maxlength":256}),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["message"].required = True
        # The guestbook row has no photo by default; a dashed circle stands in
        self.fields["icon"].required = False

    def clean_name(self):
        name = strip_tags(self.cleaned_data["name"]).strip()
        if not name:
            raise ValidationError("Name can't contain only HTML tags.")
        return name

    def clean_message(self):
        return strip_tags(self.cleaned_data["message"]).strip()
