from django.shortcuts import redirect
from django.utils.http import url_has_allowed_host_and_scheme
from django.views import View
from django.views.generic import TemplateView
from .models import WatchlistItem, Watchlist, Stock
from .services import get_market_snapshot, attach_asset_types
from django.contrib.auth.mixins import LoginRequiredMixin #Redirects to login page if user is not logged in

class HomePageView(TemplateView):
    """Displays the home page with a market snapshot and watchlist information."""
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["market_data"] = attach_asset_types(get_market_snapshot([
            "^GSPC", "^DJI", "^IXIC", "^RUT", "AAPL", "MSFT", "GOOG", "NVDA"]
            ))
    
        if self.request.user.is_authenticated:
            context["watchlist_symbols"] = set(
                Watchlist.objects.filter(user=self.request.user)
                .values_list("stocks__ticker_code", flat=True)
            )
        else:
            context["watchlist_symbols"] = set()
        return context



class WatchlistView(LoginRequiredMixin, TemplateView):
    """Displays the user's watchlist with real-time stock data."""
    template_name = "watchlist.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        watchlist, _ = Watchlist.objects.get_or_create(user=self.request.user)
        symbols = list(watchlist.stocks.values_list("ticker_code", flat=True))
        context["stocks"] = attach_asset_types(get_market_snapshot(symbols)) if symbols else []
        return context
        

class AddToWatchlistView(LoginRequiredMixin, View):
    """Add a stock to the user's watchlist."""
    http_method_names = ["post"]

    def post(self, request, *args, **kwargs):
        # Retrieves the stock symbol from the POST data, normalizes it, and adds it to the user's watchlist if valid.
        symbol = request.POST.get("symbol", "").strip().upper()
        if symbol and len(symbol) <= 15:
            stock, _ = Stock.objects.get_or_create(ticker_code=symbol)
            watchlist, _ = Watchlist.objects.get_or_create(user=request.user)
            WatchlistItem.objects.get_or_create(watchlist=watchlist, stock=stock)

        return self._redirect_back(request)

    def _redirect_back(self, request):
        # Redirects the user back to the page they came from, or to the watchlist if no valid "next" parameter is provided.
        next_url = request.POST.get("next")
        if next_url and url_has_allowed_host_and_scheme(
            next_url, allowed_hosts={request.get_host()}
        ):
            return redirect(next_url)
        return redirect("watchlist")


class RemoveFromWatchlistView(LoginRequiredMixin, View):
    """Remove a stock to the user's watchlist"""
    http_method_names = ["post"]

    def post(self, request, *args, **kwargs):
        symbol = request.POST.get("symbol", "").strip().upper()
        if symbol:
            WatchlistItem.objects.filter(
                watchlist__user=request.user,
                stock__ticker_code=symbol,
            ).delete()

        next_url = request.POST.get("next")
        if next_url and url_has_allowed_host_and_scheme(
            next_url, allowed_hosts={request.get_host()}
        ):
            return redirect(next_url)
        return redirect("watchlist")
