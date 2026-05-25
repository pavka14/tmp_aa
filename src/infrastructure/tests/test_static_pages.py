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
