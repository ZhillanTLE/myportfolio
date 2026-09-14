import json
from pathlib import Path

from django.db import migrations

FIXTURE = Path(__file__).resolve().parent.parent / 'fixtures' / 'projects.json'


def load_rows():
    with FIXTURE.open(encoding='utf-8') as f:
        return json.load(f)


def seed_projects(apps, schema_editor):
    Peer = apps.get_model('main', 'Peer')
    Project = apps.get_model('main', 'Project')

    rows = load_rows()

    for row in rows:
        if row['model'] == 'main.peer':
            Peer.objects.update_or_create(pk=row['pk'], defaults=row['fields'])

    for row in rows:
        if row['model'] == 'main.project':
            fields = dict(row['fields'])
            peer_ids = fields.pop('peers')
            project, _ = Project.objects.update_or_create(pk=row['pk'], defaults=fields)
            project.peers.set(peer_ids)


def unseed_projects(apps, schema_editor):
    Peer = apps.get_model('main', 'Peer')
    Project = apps.get_model('main', 'Project')

    rows = load_rows()
    Project.objects.filter(pk__in=[r['pk'] for r in rows if r['model'] == 'main.project']).delete()
    Peer.objects.filter(pk__in=[r['pk'] for r in rows if r['model'] == 'main.peer']).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0003_alter_peer_options_peer_order'),
    ]

    operations = [
        migrations.RunPython(seed_projects, unseed_projects),
    ]
