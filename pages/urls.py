from django.urls import path

from .views import (
    AddToWatchlistView,
    HomePageView,
    RemoveFromWatchlistView,
    WatchlistView,
    market_api_view,
)

urlpatterns = [
    path("", HomePageView.as_view(), name="home"),
    path("watchlist/", WatchlistView.as_view(), name="watchlist"),
    path("watchlist/add/", AddToWatchlistView.as_view(), name="add_to_watchlist"),
    path(
        "watchlist/remove/",
        RemoveFromWatchlistView.as_view(),
        name="remove_from_watchlist",
    ),
    path("api/market/", market_api_view, name="market_api"),
]
