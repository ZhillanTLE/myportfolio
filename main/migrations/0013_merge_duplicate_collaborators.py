from django.db import migrations


def merge_duplicates(apps, schema_editor):
    """One person, one collaborator: the Teams diagram tells people apart by id, so a second
    "Zhillan" shows up as a second person. Guestbook signatures (they carry a message) are left alone."""
    Peer = apps.get_model("main", "Peer")
    by_name = {}
    for peer in Peer.objects.filter(show_in_peers=False, message="").order_by("created_at"):
        by_name.setdefault(peer.name.strip().lower(), []).append(peer)

    for peers in by_name.values():
        if len(peers) < 2:
            continue
        # Keep whoever is on the most teams; created_at order breaks ties toward the oldest
        keeper = max(peers, key=lambda peer: peer.projects.count())
        for duplicate in peers:
            if duplicate.pk == keeper.pk:
                continue
            for project in duplicate.projects.all():
                project.peers.add(keeper)
            if not keeper.icon and duplicate.icon:
                keeper.icon = duplicate.icon
                keeper.save(update_fields=["icon"])
            duplicate.delete()


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0012_seed_experiences"),
    ]

    operations = [
        migrations.RunPython(merge_duplicates, migrations.RunPython.noop),
    ]
