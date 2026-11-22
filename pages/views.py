from django.views.generic import TemplateView
from django.http import JsonResponse
from .services import get_market_snapshot
from django.contrib.auth.mixins import LoginRequiredMixin #Redirects to login page if user is not logged in

class HomePageView(TemplateView):
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["market_data"] = get_market_snapshot(["^GSPC", "^DJI", "^IXIC", "^RUT", "AAPL", "MSFT", "GOOG", "NVDA"])
        return context

# Optional: Expose the same service as a JSON API for frontend charts or live refreshes
def market_api_view(request):
    data = get_market_snapshot()
    return JsonResponse({"results": data})

class WatchlistView(LoginRequiredMixin, TemplateView):
    template_name = "watchlist.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["stocks"] = []
        return context

