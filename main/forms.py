from django.forms import (
    CharField,
    CheckboxSelectMultiple,
    ModelForm,
    NumberInput,
    Textarea,
    TextInput,
    URLField,
    URLInput,
)
from main.models import Project, Peer
from django.core.exceptions import ValidationError
from django.utils.html import strip_tags



class ProjectForm(ModelForm):
    # Extra inputs for the "+" button; not model fields
    new_peer = CharField(
        required=False,
        widget=TextInput(attrs={"placeholder": "New Collaborator"}),
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
            "role",
            "image",
            "tech_stack",
            "peers",
            "repo_url",
            "live_url",
            "description",
            "order",
        ]

        labels = {
            "title": "Project Name",
            "year": "Year",
            "role": "Your Role",
            "image": "Image Path",
            "tech_stack": "Tech Stack",
            "peers": "Builders",
            "repo_url": "Repository Link",
            "live_url": "Live URL",
            "description": "Description",
            "order": "Display order",
        }

        widgets = {
            "title": TextInput(attrs={"placeholder": "What project??", "maxlength": 255}),
            "year": TextInput(attrs={"placeholder": "202x?", "maxlength": 16}),
            "role": TextInput(attrs={"placeholder": "Gak UIUX lagi kan?"}),
            "image": TextInput(attrs={"placeholder": "https://drive.google.com/.."}),
            "tech_stack": TextInput(attrs={"placeholder": "Next.js, Django, .."}),
            "peers": CheckboxSelectMultiple(),
            "repo_url": URLInput(attrs={"placeholder": "https://drive.google.com/..."}),
            "live_url": URLInput(attrs={"placeholder": "https://.."}),
            "description": Textarea(attrs={"placeholder": "Yapping aja lek", "rows": 6}),
            "order": NumberInput(attrs={"min":0, "placeholders":"0 = first"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name in ("role", "image", "peers"):
            self.fields[name].required = True
        self.fields["tech_stack"].required = False

    def clean_title(self):
        title = strip_tags(self.cleaned_data["title"]).strip()
        if not title:
            raise ValidationError("Project name can't contain only HTML tags.")
        return title

    def clean_tech_stack(self):
        return strip_tags(self.cleaned_data["tech_stack"]).strip()

    def clean_description(self):
        return strip_tags(self.cleaned_data["description"]).strip()


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