from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin #Redirects to login page if user is not logged in

class HomePageView(TemplateView):
    template_name = "home.html"

class WatchlistView(LoginRequiredMixin, TemplateView):
    template_name = "watchlist.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["stocks"] = []
        return context