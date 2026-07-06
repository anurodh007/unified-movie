from django.urls import path

from watchlist.views import WatchlistListCreateAPIView, WatchlistDestroyAPIView


urlpatterns = [
    path('', WatchlistListCreateAPIView.as_view(), name='user-watchlist'),
    path('<int:tmdb_id>/', WatchlistDestroyAPIView.as_view(), name='user-watchlist-delete'),
]