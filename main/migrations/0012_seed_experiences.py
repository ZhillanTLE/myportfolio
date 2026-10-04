import datetime

from django.db import migrations

# The four roles that used to be hard-coded in projects.html, now served from the database
EXPERIENCES = [
    {
        "pk": "6f1c2a8e-3b4d-4e5f-9a10-000000000001",
        "title": "Product Management Intern @ Opsigo Asia",
        "organization": "Opsigo Asia · Jakarta",
        "category": "internship",
        "started_at": datetime.date(2026, 7, 1),
        "ended_at": datetime.date(2026, 8, 31),
        "description": (
            "Researched and shipped a consolidated multi-item cart, replacing the repeated search-and-compare cycle "
            "across flights, hotels, and rail with a single flow · a projected 66.6% drop in admin work per itinerary.\n"
            "Led a High/Standard/Low fare-tiering feature that auto-ranks search results with QuickSelect partitioning, "
            "cutting manual price benchmarking and reducing SLA response time per item search by 75%."
        ),
    },
    {
        "pk": "6f1c2a8e-3b4d-4e5f-9a10-000000000002",
        "title": "Manager of Website Development @ OH Fasilkom UI",
        "organization": "Open House Fasilkom UI · Depok",
        "category": "volunteer",
        "started_at": datetime.date(2026, 2, 1),
        "ended_at": None,
        "description": "Memecut IT Dev & UIUX\nMemasak PRD\nCLARITYYY INNN TECHNOLOGYYYY!!",
    },
    {
        "pk": "6f1c2a8e-3b4d-4e5f-9a10-000000000003",
        "title": "Technical Project Manager @ Tinta, a GEMASTIK project",
        "organization": "GEMASTIK 2026 · Indonesia",
        "category": "research",
        "started_at": datetime.date(2026, 5, 1),
        "ended_at": datetime.date(2026, 5, 31),
        "description": (
            "I LOVE ZAYYAN AND NIA\n"
            "Served as Technical Product Manager, leading the technical architecture for a 3-person CS team building "
            "an academic writing integrity platform for Indonesian higher education\n"
            "Designed a full-stack system featuring role-based access control, real-time collaboration, "
            "and a process-basedwriting verification approach"
        ),
    },
    {
        "pk": "6f1c2a8e-3b4d-4e5f-9a10-000000000004",
        "title": "Head of UIUX @ ARUNG Fasilkom UI",
        "organization": "Website Angkatan Fasilkom UI 2025 · Depok",
        "category": "volunteer",
        "started_at": datetime.date(2025, 10, 1),
        "ended_at": datetime.date(2025, 12, 31),
        "description": (
            "Lead UIUX Team to research, plan, wireframe, and final design to complete Fasilkom UI 2025 "
            "Cohort's website serving 400+ cohort members"
        ),
    },
]


def seed_experiences(apps, schema_editor):
    Experience = apps.get_model("main", "Experience")
    for row in EXPERIENCES:
        fields = dict(row)
        Experience.objects.update_or_create(pk=fields.pop("pk"), defaults=fields)


def unseed_experiences(apps, schema_editor):
    Experience = apps.get_model("main", "Experience")
    Experience.objects.filter(pk__in=[row["pk"] for row in EXPERIENCES]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0011_experience_org_dates_stars"),
    ]

    operations = [
        migrations.RunPython(seed_experiences, unseed_experiences),
    ]
