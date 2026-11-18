from django.urls import path 

from .views import HomePageView, WatchlistView

urlpatterns = [ 
path("", HomePageView.as_view(), name="home"),
path("watchlist/", WatchlistView.as_view(), name="watchlist"),
]