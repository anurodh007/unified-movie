from django.urls import path

from watchlist.views import WatchlistListCreateAPIView


urlpatterns = [
    path('', WatchlistListCreateAPIView.as_view(), name='user-watchlist')
]