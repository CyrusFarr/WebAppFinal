from typing import Any

from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.shortcuts import redirect
from django.http import JsonResponse
from pages.models import Watchlist
from .services import get_market_snapshot


class HomePageView(TemplateView):
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["market_data"] = get_market_snapshot(
            ["^GSPC", "^DJI", "^IXIC", "^RUT", "AAPL", "MSFT", "GOOG", "NVDA"]
        )
        return context


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)

        context["market_data"] = get_market_snapshot(["AAPL", "MSFT", "GOOG", "NVDA"])

        return context


# Expose market data as a JSON API
def market_api_view(request):
    data = get_market_snapshot()
    return JsonResponse({"results": data})


class WatchlistView(LoginRequiredMixin, TemplateView):
    template_name = "watchlist.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        stocks = Watchlist.objects.filter(user=self.request.user).order_by("symbol")

        symbols = list(stocks.values_list("symbol", flat=True))

        context["stocks"] = stocks
        context["market_data"] = get_market_snapshot(symbols) if symbols else []

        return context


# Only authenticated users can add stocks
@login_required
@require_POST
def add_to_watchlist(request):
    symbol = request.POST.get("symbol", "").strip().upper()

    allowed_symbols = [
        "AAPL",
        "GOOGL",
        "GOOG",
        "MSFT",
        "AMZN",
        "TSLA",
        "NVDA",
        "^GSPC",
        "^DJI",
        "^IXIC",
        "^RUT",
    ]

    if symbol in allowed_symbols:
        Watchlist.objects.get_or_create(user=request.user, symbol=symbol)

    return redirect("watchlist")


# Only authenticated users can remove stocks
@login_required
@require_POST
def remove_from_watchlist(request):
    symbol = request.POST.get("symbol", "").strip().upper()

    Watchlist.objects.filter(user=request.user, symbol=symbol).delete()

    return redirect("watchlist")
