from django.urls import path

from .views import HomePageView, WatchlistView
from .views import add_to_watchlist, remove_from_watchlist
from .views import market_api_view

urlpatterns = [
    path("", HomePageView.as_view(), name="home"),
    path("watchlist/", WatchlistView.as_view(), name="watchlist"),
    path("watchlist/add/", add_to_watchlist, name="add_to_watchlist"),
    path("watchlist/remove/", remove_from_watchlist, name="remove_from_watchlist"),
    path("api/market/", market_api_view, name="market_api"),
]
