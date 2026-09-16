from django.forms import (
    CharField,
    CheckboxSelectMultiple,
    ModelForm,
    Textarea,
    TextInput,
    URLField,
    URLInput,
)
from main.models import Project


class ProjectForm(ModelForm):
    # Extra inputs for the "+" button; not model fields
    new_peer = CharField(
        required=False,
        widget=TextInput(attrs={"placeholder": "New Collaborator"}),
    )
    new_peer_icon = URLField(
        required=False,
        widget=URLInput(attrs={"placeholder": "Photo URL"}),
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
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name in ("role", "image", "peers"):
            self.fields[name].required = True
        self.fields["tech_stack"].required = False
