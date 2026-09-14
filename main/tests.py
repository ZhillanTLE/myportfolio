from django.test import TestCase
from django.urls import reverse

from main.models import Peer, Project


class MainTest(TestCase):
    def setUp(self):
        self.peer = Peer.objects.create(
            name="Zayyan",
            icon="icons/peers/zayyanicon.jpeg",
        )
        self.project = Project.objects.create(
            title="Tinta",
            year="2026",
            role="Technical Project Manager",
            description="Academic writing integrity platform.",
            image="img/projects/TintaSnapshot.jpeg",
            tech_stack="Django, Postgres, React",
            repo_url="https://github.com/example/tinta",
            live_url="https://tinta.example.com",
        )
        self.project.peers.add(self.peer)

    def test_main_url_is_accessible(self):
        response = self.client.get(reverse("main:show_main"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "index.html")
        self.assertContains(response, f'href="{reverse("main:show_projects")}"')

    def test_nonexistent_page_returns_404(self):
        response = self.client.get("/halaman-yang-tidak-ada/")

        self.assertEqual(response.status_code, 404)

    def test_project_model(self):
        self.assertEqual(str(self.project), "Tinta")
        self.assertEqual(self.project.tech_list, ["Django", "Postgres", "React"])
        self.assertIn(self.peer, self.project.peers.all())

    def test_projects_url_uses_correct_template(self):
        response = self.client.get(reverse("main:show_projects"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "projects.html")

    def test_projects_page_shows_model_data(self):
        response = self.client.get(reverse("main:show_projects"))

        self.assertContains(response, self.project.title)
        self.assertContains(response, self.project.description)
        self.assertContains(response, self.project.year)
        self.assertContains(response, "Django + Postgres + React")
        self.assertContains(response, self.project.repo_url)
        self.assertContains(response, self.project.live_url)
        self.assertContains(response, self.peer.name)
        self.assertContains(response, f'href="{reverse("main:show_main")}"')
        self.assertNotContains(response, "No projects added yet.")

    def test_projects_page_shows_empty_state(self):
        Project.objects.all().delete()
        response = self.client.get(reverse("main:show_projects"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No projects added yet.")
        self.assertNotContains(response, "Tinta")

    def test_peers_render_in_order(self):
        last = Peer.objects.create(name="Nia", icon="icons/peers/niaicon.jpeg", order=2)
        first = Peer.objects.create(name="Bagas", icon="icons/peers/bagasicon.jpeg", order=1)
        self.project.peers.add(last, first)
        response = self.client.get(reverse("main:show_projects"))
        html = response.content.decode()

        self.assertLess(html.index("Zayyan"), html.index("Bagas"))
        self.assertLess(html.index("Bagas"), html.index("Nia"))
