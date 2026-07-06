from django.db import models
from django.db.models import UniqueConstraint
from users.models import User
from movies.models import Movie


class Watchlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='watchlist')
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='watchlisted_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=('user', 'movie'),
                name='unique_user_movie_watchlist'
            )
        ]