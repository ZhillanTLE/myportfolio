import datetime
import uuid

from django.contrib.auth.models import Group, Permission, User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from main.models import Experience, Project


class ProjectAPITest(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_superuser(
            username="owner", password="test-password", email="owner@example.com",
        )
        self.visitor = User.objects.create_user(username="visitor", password="test-password")
        Project.objects.all().delete()   # data migrations seed the real projects
        self.project = Project.objects.create(
            title="Portfolio", year="2026", description="My website", tech_stack="Django",
        )
        self.list_url = reverse("api:project-list")
        self.detail_url = reverse("api:project-detail", args=[self.project.id])
        self.star_url = reverse("api:project-star", args=[self.project.id])
        self.payload = {
            "title": "New project", "year": "2026", "description": "A useful app",
            "tech_stack": "Python", "live_url": "https://example.com/", "image": "",
        }

    def test_public_list_and_detail(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["id"], str(self.project.id))
        self.assertFalse(response.data[0]["is_starred"])
        self.assertNotIn("fields", response.data[0])
        self.assertEqual(self.client.get(self.detail_url).status_code, status.HTTP_200_OK)

    def test_search_and_empty_results(self):
        response = self.client.get(self.list_url, {"title": "PORT"})
        self.assertEqual(len(response.data), 1)
        response = self.client.get(self.list_url, {"title": "not-found"})
        self.assertEqual(response.data, [])

    def test_missing_project(self):
        url = reverse("api:project-detail", args=[uuid.uuid4()])
        self.assertEqual(self.client.get(url).status_code, status.HTTP_404_NOT_FOUND)

    def test_guest_and_visitor_cannot_write(self):
        for user in (None, self.visitor):
            self.client.force_authenticate(user=user)
            self.assertEqual(self.client.post(self.list_url, self.payload, format="json").status_code, 403)
            self.assertEqual(self.client.patch(self.detail_url, {"title": "Changed"}, format="json").status_code, 403)
            self.assertEqual(self.client.delete(self.detail_url).status_code, 403)
        self.assertEqual(Project.objects.count(), 1)
        self.project.refresh_from_db()
        self.assertEqual(self.project.title, "Portfolio")

    def test_owner_can_create(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(self.list_url, self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Project.objects.filter(pk=response.data["id"]).exists())

    def test_validation(self):
        self.client.force_authenticate(user=self.owner)
        for changes, field in [
            ({"title": "   "}, "title"),
            ({"title": '<img src="x" onerror="alert(1)">'}, "title"),
            ({"live_url": "javascript:alert(1)"}, "live_url"),
        ]:
            response = self.client.post(self.list_url, {**self.payload, **changes}, format="json")
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn(field, response.data)
        self.assertEqual(Project.objects.count(), 1)

    def test_patch_put_and_delete(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.patch(self.detail_url, {"title": "Changed"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.project.refresh_from_db()
        self.assertEqual(self.project.description, "My website")
        response = self.client.put(self.detail_url, {"title": "Incomplete"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response = self.client.put(self.detail_url, self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(response.content, b"")
        self.assertFalse(Project.objects.filter(pk=self.project.id).exists())

    def test_star_requires_login_and_toggles(self):
        self.assertEqual(self.client.post(self.star_url).status_code, status.HTTP_403_FORBIDDEN)
        self.client.force_authenticate(user=self.visitor)
        response = self.client.post(self.star_url)
        self.assertTrue(response.data["is_starred"])
        self.assertEqual(response.data["star_count"], 1)
        response = self.client.post(self.star_url)
        self.assertFalse(response.data["is_starred"])
        self.assertEqual(response.data["star_count"], 0)

    def test_computed_fields_are_read_only(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(self.list_url, {
            **self.payload, "star_count": 99, "is_starred": True,
            "starred_by_names": "forged", "starred_by": [self.visitor.id],
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["star_count"], 0)
        self.assertFalse(response.data["is_starred"])

    def test_staff_and_editor_cannot_manage_tutorial_projects(self):
        self.visitor.is_staff = True
        self.visitor.save()
        self.visitor.groups.add(Group.objects.create(name="Editor"))
        self.client.force_authenticate(user=self.visitor)
        response = self.client.patch(self.detail_url, {"title": "Changed"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_wrong_method(self):
        self.client.force_authenticate(user=self.owner)
        self.assertEqual(self.client.delete(self.list_url).status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_session_write_without_csrf_is_rejected(self):
        client = APIClient(enforce_csrf_checks=True)
        self.assertTrue(client.login(username="owner", password="test-password"))
        response = client.post(self.list_url, self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Project.objects.count(), 1)

    def test_session_write_with_csrf_succeeds(self):
        client = APIClient(enforce_csrf_checks=True)
        client.login(username="owner", password="test-password")
        # The Browsable API form renders a real CSRF token into the response.
        page = client.get(self.list_url, HTTP_ACCEPT="text/html")
        self.assertEqual(page.status_code, status.HTTP_200_OK)
        token = client.cookies["csrftoken"].value
        response = client.post(
            self.list_url, self.payload, format="json", HTTP_X_CSRFTOKEN=token,
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class ExperienceAPITest(APITestCase):
    """Experience is this portfolio's own section. Four roles:

    visitor reads; a logged-in user reads and stars; an Editor also PUT/PATCHes;
    only the owner (superuser) creates and deletes.
    """

    def setUp(self):
        Experience.objects.all().delete()   # migration 0012 seeds the real roles
        self.owner = User.objects.create_superuser(username="owner", password="test-password")
        self.user = User.objects.create_user(username="visitor", password="test-password")
        # Editor is the Tugas 4 role: a group holding change_experience, checked with has_perm
        editors = Group.objects.create(name="Editor")
        editors.permissions.add(Permission.objects.get(codename="change_experience"))
        self.editor = User.objects.create_user(username="editor", password="test-password")
        self.editor.groups.add(editors)

        self.experience = Experience.objects.create(
            title="Intern", organization="Opsigo", category="internship",
            started_at=datetime.date(2026, 7, 1), description="Shipped a cart.",
        )
        self.list_url = reverse("api:experience-list")
        self.detail_url = reverse("api:experience-detail", args=[self.experience.id])
        self.star_url = reverse("api:experience-star", args=[self.experience.id])
        self.payload = {
            "title": "Asisten Dosen", "organization": "Fasilkom UI", "category": "part-time",
            "started_at": "2026-09-01", "ended_at": None, "description": "Taught calculus.",
        }

    def assertUnchanged(self):
        """A refused write must leave the database exactly as it was."""
        self.assertEqual(Experience.objects.count(), 1)
        self.experience.refresh_from_db()
        self.assertEqual(self.experience.title, "Intern")

    # Reading

    def test_everyone_can_read_list_and_detail(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["id"], str(self.experience.id))
        self.assertEqual(response.data[0]["period"], "JUL–NOW '26")
        self.assertEqual(self.client.get(self.detail_url).status_code, status.HTTP_200_OK)

    def test_no_account_data_leaks(self):
        self.experience.starred_by.add(self.user)
        data = self.client.get(self.detail_url).data
        self.assertNotIn("starred_by", data)
        self.assertNotIn("visitor", str(data))

    def test_search_by_title_or_organization(self):
        self.assertEqual(len(self.client.get(self.list_url, {"q": "intern"}).data), 1)
        self.assertEqual(len(self.client.get(self.list_url, {"q": "opsigo"}).data), 1)
        response = self.client.get(self.list_url, {"q": "nothing-here"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])

    def test_missing_experience_is_404(self):
        url = reverse("api:experience-detail", args=[uuid.uuid4()])
        self.assertEqual(self.client.get(url).status_code, status.HTTP_404_NOT_FOUND)
        self.client.force_authenticate(user=self.owner)
        self.assertEqual(self.client.patch(url, {"title": "X"}, format="json").status_code, 404)

    # Roles

    def test_guest_and_user_cannot_write(self):
        for account in (None, self.user):
            self.client.force_authenticate(user=account)
            self.assertEqual(self.client.post(self.list_url, self.payload, format="json").status_code, 403)
            self.assertEqual(self.client.patch(self.detail_url, {"title": "X"}, format="json").status_code, 403)
            self.assertEqual(self.client.put(self.detail_url, self.payload, format="json").status_code, 403)
            self.assertEqual(self.client.delete(self.detail_url).status_code, 403)
        self.assertUnchanged()

    def test_editor_can_patch_and_put(self):
        self.client.force_authenticate(user=self.editor)
        response = self.client.patch(self.detail_url, {"title": "Lead intern"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.experience.refresh_from_db()
        self.assertEqual(self.experience.title, "Lead intern")
        self.assertEqual(self.experience.organization, "Opsigo")   # PATCH keeps what wasn't sent
        response = self.client.put(self.detail_url, self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.experience.refresh_from_db()
        self.assertEqual(self.experience.organization, "Fasilkom UI")

    def test_editor_cannot_create_or_delete(self):
        self.client.force_authenticate(user=self.editor)
        self.assertEqual(self.client.post(self.list_url, self.payload, format="json").status_code, 403)
        self.assertEqual(self.client.delete(self.detail_url).status_code, 403)
        self.assertUnchanged()

    def test_owner_can_create_and_delete(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(self.list_url, self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Experience.objects.filter(pk=response.data["id"], title="Asisten Dosen").exists())
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(response.content, b"")
        self.assertFalse(Experience.objects.filter(pk=self.experience.id).exists())

    def test_put_needs_every_required_field(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.put(self.detail_url, {"title": "Only a title"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("started_at", response.data)
        self.assertUnchanged()

    # Validation

    def test_text_is_stripped_of_tags(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(self.list_url, {
            **self.payload, "title": "<b>Asisten</b> Dosen", "organization": "<i>Fasilkom</i>",
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        created = Experience.objects.get(pk=response.data["id"])
        self.assertEqual(created.title, "Asisten Dosen")
        self.assertEqual(created.organization, "Fasilkom")

    def test_invalid_input_is_400_and_not_saved(self):
        self.client.force_authenticate(user=self.owner)
        for changes, field in [
            ({"title": "   "}, "title"),
            ({"title": '<img src="x" onerror="alert(1)">'}, "title"),
            ({"description": "<p></p>"}, "description"),
            ({"category": "astronaut"}, "category"),
            ({"started_at": "not-a-date"}, "started_at"),
            ({"started_at": "2026-09-01", "ended_at": "2026-01-01"}, "ended_at"),
        ]:
            response = self.client.post(self.list_url, {**self.payload, **changes}, format="json")
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, changes)
            self.assertIn(field, response.data)
        self.assertUnchanged()

    def test_patch_end_before_existing_start_is_rejected(self):
        self.client.force_authenticate(user=self.editor)
        response = self.client.patch(self.detail_url, {"ended_at": "2026-01-01"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("ended_at", response.data)
        self.experience.refresh_from_db()
        self.assertIsNone(self.experience.ended_at)

    def test_computed_fields_are_read_only(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(self.list_url, {
            **self.payload, "star_count": 99, "is_starred": True, "period": "forged",
            "starred_by": [self.user.id],
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["star_count"], 0)
        self.assertFalse(response.data["is_starred"])
        self.assertFalse(Experience.objects.get(pk=response.data["id"]).starred_by.exists())

    # Star

    def test_guest_cannot_star(self):
        self.assertEqual(self.client.post(self.star_url).status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(self.experience.starred_by.exists())

    def test_star_toggles_for_the_caller_only(self):
        self.client.force_authenticate(user=self.user)
        # A forged user id in the body is ignored: the star always belongs to request.user
        response = self.client.post(self.star_url, {"user": self.owner.id}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["is_starred"])
        self.assertEqual(response.data["star_count"], 1)
        self.assertEqual(list(self.experience.starred_by.all()), [self.user])
        response = self.client.post(self.star_url)
        self.assertFalse(response.data["is_starred"])
        self.assertEqual(response.data["star_count"], 0)

    def test_star_is_post_only_and_404_for_missing(self):
        self.client.force_authenticate(user=self.user)
        self.assertEqual(self.client.get(self.star_url).status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        missing = reverse("api:experience-star", args=[uuid.uuid4()])
        self.assertEqual(self.client.post(missing).status_code, status.HTTP_404_NOT_FOUND)

    # CSRF, with a real session login (force_authenticate skips CSRF)

    def test_session_write_without_csrf_is_rejected(self):
        client = APIClient(enforce_csrf_checks=True)
        self.assertTrue(client.login(username="owner", password="test-password"))
        self.assertEqual(client.post(self.list_url, self.payload, format="json").status_code, 403)
        self.assertEqual(client.post(self.star_url).status_code, 403)
        self.assertUnchanged()
        self.assertFalse(self.experience.starred_by.exists())

    def test_session_write_with_csrf_succeeds(self):
        client = APIClient(enforce_csrf_checks=True)
        self.assertTrue(client.login(username="editor", password="test-password"))
        client.get(reverse("main:show_projects"))   # the page sets the csrftoken cookie
        token = client.cookies["csrftoken"].value
        response = client.patch(self.detail_url, {"title": "Lead intern"}, format="json", HTTP_X_CSRFTOKEN=token)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class ExperiencePageTest(APITestCase):
    """The page only shows the controls each role can actually use."""

    def setUp(self):
        self.owner = User.objects.create_superuser(username="owner", password="test-password")
        self.editor = User.objects.create_user(username="editor", password="test-password")
        self.editor.user_permissions.add(Permission.objects.get(codename="change_experience"))
        self.url = reverse("main:show_projects")

    def test_visitor_gets_no_modal(self):
        response = self.client.get(self.url)
        self.assertNotContains(response, 'id="add-experience-modal"')
        self.assertContains(response, reverse("api:experience-list"))

    def test_editor_gets_edit_modal_but_no_add_button(self):
        self.client.force_login(self.editor)
        response = self.client.get(self.url)
        self.assertContains(response, 'id="add-experience-modal"')
        self.assertNotContains(response, 'id="experience-add"')

    def test_owner_gets_add_button(self):
        self.client.force_login(self.owner)
        self.assertContains(self.client.get(self.url), 'id="experience-add"')
