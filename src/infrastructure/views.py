from django.views.generic import TemplateView


class NavigationTemplateView(TemplateView):
    page_key = ""
    page_title = ""

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_key"] = self.page_key
        context["page_title"] = self.page_title
        return context


class HomeView(NavigationTemplateView):
    template_name = "infrastructure/home.html"
    page_key = "home"
    page_title = "AA Test Site"


class DocsView(NavigationTemplateView):
    template_name = "infrastructure/docs.html"
    page_key = "docs"
    page_title = "Documentation"


class ApiView(NavigationTemplateView):
    template_name = "infrastructure/api.html"
    page_key = "api"
    page_title = "API Specifications"
