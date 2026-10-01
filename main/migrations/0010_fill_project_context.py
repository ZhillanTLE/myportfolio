from django.db import migrations

# Context lines for the projects that existed before Project.context did
CONTEXT = {
    "Windfall": "Ranked 6 of 250+ at AIC COMPFEST 18",
    "Arung's Website": "Cohort site serving 400+ members",
    "Tinta": "GEMASTIK 2026 · 3-person CS team",
}
# Windfall's description opened with its ranking, which now lives in context
WINDFALL_RANKING = "MVP Ranked 6 / 250++ in AIC COMPFEST 18."


def fill_context(apps, schema_editor):
    Project = apps.get_model("main", "Project")
    for project in Project.objects.filter(title__in=CONTEXT, context=""):
        project.context = CONTEXT[project.title]
        if project.description.startswith(WINDFALL_RANKING):
            project.description = project.description[len(WINDFALL_RANKING):].lstrip()
        if project.title == "Arung's Website" and not project.role:
            project.role = "Head of UIUX"
        project.save()


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0009_project_context_peer_icon_optional"),
    ]

    operations = [
        migrations.RunPython(fill_context, migrations.RunPython.noop),
    ]
