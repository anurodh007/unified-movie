from django.db import models
from django.db.models import UniqueConstraint
from users.models import User
from movies.models import Movie


class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_reviews')
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='movie_reviews')
    review_text = models.TextField()
    rating = models.PositiveSmallIntegerField()

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            UniqueConstraint(fields=('user', 'movie'), name='unique_user_movie_review')
        ]

    def __str__(self):
        return f'{self.user.username} - {self.movie.title}'
    

class ReviewLike(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        constraints = [
            UniqueConstraint(fields=('user', 'review'), name='unique_user_review_like')
        ]


class ReviewComment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='comments')
    comment_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)