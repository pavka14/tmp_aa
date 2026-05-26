from django.contrib.auth import get_user_model
from django.contrib.staticfiles.views import serve
from django.test import RequestFactory, TestCase


class TestStaticWebsitePages(TestCase):
    def test_static_pages_and_static_asset_load(self):
        pages = [
            ("/", "AA Test Site", "navbar navbar-expand-lg navbar-light bg-light"),
            ("/docs/", "Documentation", 'class="nav-link active" href="/docs/"'),
            ("/api/", "API Specifications", 'class="nav-link active" href="/api/"'),
        ]

        for path, title, style_marker in pages:
            response = self.client.get(path)
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, f"<title>{title}</title>")
            self.assertContains(response, style_marker)

        request = RequestFactory().get("/static/infrastructure/site.css")
        static_response = serve(request, "infrastructure/site.css", insecure=True)
        self.assertEqual(static_response.status_code, 200)
        static_content = b"".join(static_response.streaming_content).decode()
        self.assertIn("background-color", static_content)

    def test_home_shows_login_prompt_for_anonymous(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "const isAuthenticated = false;")
        self.assertContains(
            response,
            'Please <a href="${homeUrls.admin}">log in</a> and reload',
        )

    def test_home_sets_authenticated_flag_for_logged_in_user(self):
        user_model = get_user_model()
        user = user_model.objects.create_user(username="viewer")
        self.client.force_login(user)

        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "const isAuthenticated = true;")

    def test_docs_page_renders_readme_html(self):
        response = self.client.get("/docs/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "<h1>Temporary test repository</h1>")
