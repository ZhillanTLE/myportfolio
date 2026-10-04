from django.test import TestCase
from django.urls import reverse

from main.models import Experience, Peer, Project


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


class TeamsAndGuestbookTest(TestCase):
    def setUp(self):
        from django.contrib.auth.models import User

        # Migration 0004 seeds the real projects and peers; start from nothing
        Project.objects.all().delete()
        Peer.objects.all().delete()
        self.zhillan = Peer.objects.create(name="Zhillan", icon="icons/peers/zhillanicon.jpeg")
        self.others = Peer.objects.create(name="+34 Others", icon="icons/peers/plusicon.jpeg")
        self.arung = Project.objects.create(
            title="Arung", year="2025", role="Head of UIUX", context="Cohort site",
            description="A cohort site.", image="img/projects/ArungSnapshot.jpeg", tech_stack="",
        )
        self.arung.peers.add(self.zhillan, self.others)
        self.admin = User.objects.create_superuser("owner", password="pw-owner-123")

    def test_team_label_counts_placeholder_peers(self):
        self.assertEqual(self.arung.team_label, "1 + 34 others")

    def test_projects_json_has_role_context_team(self):
        fields = self.client.get(reverse("main:get_projects_json")).json()[0]["fields"]
        self.assertEqual(fields["context"], "Cohort site")
        self.assertEqual(fields["team_label"], "1 + 34 others")
        self.assertIn("pk", fields["peers"][0])

    def test_add_teammate_needs_permission(self):
        response = self.client.post(reverse("main:add_teammate"), {"name": "Lefi", "projects": [self.arung.pk]})
        self.assertEqual(response.status_code, 403)

    def test_add_teammate_reuses_collaborator_not_guest(self):
        Peer.objects.create(name="Zhillan", message="hi", show_in_peers=True)
        self.client.force_login(self.admin)
        response = self.client.post(reverse("main:add_teammate"), {"name": "zhillan", "projects": [self.arung.pk]})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["pk"], str(self.zhillan.pk))
        self.assertEqual(Peer.objects.filter(show_in_peers=False, name__iexact="zhillan").count(), 1)

    def test_add_teammate_requires_a_team(self):
        self.client.force_login(self.admin)
        response = self.client.post(reverse("main:add_teammate"), {"name": "Lefi"})
        self.assertEqual(response.status_code, 400)

    def test_project_form_accepts_new_builder_instead_of_chip(self):
        self.client.force_login(self.admin)
        response = self.client.post(reverse("main:create_project_ajax"), {
            "title": "Windfall", "year": "2026", "image": "img/projects/WindfallSnapshot2.jpeg",
            "role": "AI Engineer", "context": "Ranked 6", "description": "Rebuilds carts.",
            "new_peer": "Micguel",
        })
        self.assertEqual(response.status_code, 201)
        project = Project.objects.get(title="Windfall")
        self.assertEqual([p.name for p in project.peers.all()], ["Micguel"])

    def test_project_form_needs_a_builder(self):
        self.client.force_login(self.admin)
        response = self.client.post(reverse("main:create_project_ajax"), {
            "title": "Windfall", "year": "2026", "image": "x.png", "role": "AI", "context": "c", "description": "d",
        })
        self.assertEqual(response.status_code, 400)
        self.assertIn("peers", response.json()["errors"])

    def test_guestbook_signs_with_fetch_and_renders(self):
        response = self.client.post(
            reverse("main:create_peer"), {"name": "Tania", "message": "<b>hello</b>"},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["message"], "hello")
        self.assertEqual(response.json()["icon_url"], "")
        page = self.client.get(reverse("main:show_projects")).content.decode()
        self.assertIn('<span class="nm">Tania</span>', page)
        self.assertIn('id="sign-no">02<', page)


class ExperienceAjaxTest(TestCase):
    def setUp(self):
        import datetime
        from django.contrib.auth.models import User

        # Migration 0012 seeds the real roles; start from nothing
        Experience.objects.all().delete()
        self.opsigo = Experience.objects.create(
            title="Product Management Intern", organization="Opsigo Asia · Jakarta", category="internship",
            started_at=datetime.date(2026, 7, 1), ended_at=datetime.date(2026, 8, 31),
            description="Shipped a cart.\nRanked fares.",
        )
        self.admin = User.objects.create_superuser("owner", password="pw-owner-123")
        self.visitor = User.objects.create_user("visitor", password="pw-visitor-123")
        self.valid = {
            "title": "Asisten Dosen", "organization": "Fasilkom UI", "category": "part-time",
            "started_at": "2026-09-01", "ended_at": "", "description": "Taught calculus.",
        }

    def test_period_label(self):
        import datetime
        self.assertEqual(self.opsigo.period, "JUL–AUG '26")
        self.opsigo.ended_at = None
        self.assertEqual(self.opsigo.period, "JUL–NOW '26")
        self.opsigo.ended_at = datetime.date(2026, 7, 20)
        self.assertEqual(self.opsigo.period, "JUL '26")
        self.opsigo.ended_at = datetime.date(2027, 1, 5)
        self.assertEqual(self.opsigo.period, "JUL '26–JAN '27")

    def test_page_is_a_skeleton_for_visitors(self):
        response = self.client.get(reverse("main:show_projects"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'id="experience-list"')
        self.assertNotContains(response, self.opsigo.title)
        self.assertNotContains(response, 'id="add-experience-modal"')

    def test_editor_gets_the_modal(self):
        self.client.force_login(self.admin)
        response = self.client.get(reverse("main:show_projects"))
        self.assertContains(response, 'id="add-experience-modal"')

    def test_json_for_visitor_has_stars_but_not_starred(self):
        self.opsigo.starred_by.add(self.admin)
        fields = self.client.get(reverse("main:get_experiences_json")).json()[0]["fields"]
        self.assertEqual(fields["star_count"], 1)
        self.assertFalse(fields["is_starred"])
        self.assertEqual(fields["points"], ["Shipped a cart.", "Ranked fares."])
        self.assertEqual(fields["category_label"], "Internship")

    def test_json_marks_my_star(self):
        self.opsigo.starred_by.add(self.visitor)
        self.client.force_login(self.visitor)
        fields = self.client.get(reverse("main:get_experiences_json")).json()[0]["fields"]
        self.assertTrue(fields["is_starred"])

    def test_json_search_by_title_or_organization(self):
        url = reverse("main:get_experiences_json")
        self.assertEqual(len(self.client.get(url, {"q": "intern"}).json()), 1)
        self.assertEqual(len(self.client.get(url, {"q": "opsigo"}).json()), 1)
        self.assertEqual(self.client.get(url, {"q": "nothing like it"}).json(), [])

    def test_create_needs_permission(self):
        url = reverse("main:create_experience_ajax")
        self.assertEqual(self.client.post(url, self.valid).status_code, 403)
        self.client.force_login(self.visitor)
        self.assertEqual(self.client.post(url, self.valid).status_code, 403)
        self.assertFalse(Experience.objects.filter(title="Asisten Dosen").exists())

    def test_create_returns_201_and_strips_tags(self):
        self.client.force_login(self.admin)
        data = dict(self.valid, title="<script>alert(1)</script>Asisten Dosen", description="<b>Taught</b> calculus.")
        response = self.client.post(reverse("main:create_experience_ajax"), data)
        self.assertEqual(response.status_code, 201)
        experience = Experience.objects.get(pk=response.json()["pk"])
        self.assertEqual(experience.title, "alert(1)Asisten Dosen")
        self.assertEqual(experience.description, "Taught calculus.")
        self.assertTrue(experience.is_ongoing)

    def test_create_rejects_bad_input_with_400(self):
        self.client.force_login(self.admin)
        data = dict(self.valid, title="<b></b>", started_at="2026-09-01", ended_at="2026-08-01")
        response = self.client.post(reverse("main:create_experience_ajax"), data)
        self.assertEqual(response.status_code, 400)
        self.assertIn("title", response.json()["errors"])
        self.assertIn("ended_at", response.json()["errors"])

    def test_create_requires_csrf_token(self):
        from django.test import Client
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.admin)
        self.assertEqual(client.post(reverse("main:create_experience_ajax"), self.valid).status_code, 403)

    def test_star_toggles_for_logged_in_user_only(self):
        url = reverse("main:toggle_experience_star", args=[self.opsigo.pk])
        self.assertEqual(self.client.post(url).status_code, 403)
        self.client.force_login(self.visitor)
        self.assertEqual(self.client.post(url).json(), {"is_starred": True, "star_count": 1})
        self.assertEqual(self.client.post(url).json(), {"is_starred": False, "star_count": 0})
