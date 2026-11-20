from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.shortcuts import redirect
from pages.models import Watchlist


class HomePageView(TemplateView):
    template_name = "home.html"


class WatchlistView(LoginRequiredMixin, TemplateView):
    template_name = "watchlist.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["stocks"] = Watchlist.objects.filter(user=self.request.user).order_by(
            "symbol"
        )
        return context


# only users can save to watchlist
@login_required
# prevents adding stocks to watchlist via GET request
@require_POST
def add_to_watchlist(request):
    symbol = request.POST.get("symbol", "").strip().upper()

    allowed_symbols = ["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA"]

    if symbol in allowed_symbols:
        Watchlist.objects.get_or_create(user=request.user, symbol=symbol)

    return redirect("watchlist")


def remove_from_watchlist(request):
    symbol = request.POST.get("symbol", "").strip().upper()

    Watchlist.objects.filter(user=request.user, symbol=symbol).delete()

    return redirect("watchlist")
