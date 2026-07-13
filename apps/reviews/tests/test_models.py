"""
Test Review Model

Covers:
    - String Representation
    - One review per user per movie
    - Created and Updated Changes
    - Cascading user/movie delete
    - One like per review per user
    - Comment Creation
"""


import pytest
from django.db import IntegrityError


"""
Review model
"""
@pytest.mark.django_db
class TestReviewModel:

    def test_str_representation_returns_username_movie_title(self, user_factory, movie_factory, review_factory):
        user = user_factory(username='anurodh', email='anurodh@gmail.com')
        movie = movie_factory(tmdb_id=550, title='Fight Club')
        review = review_factory(user=user, movie=movie, review_text='The First Rule', rating=9)
        assert str(review) == 'anurodh - Fight Club'

    def test_unique_user_movie_review_constraint(self, user_factory, movie_factory, review_factory):
        user = user_factory(username='alice', email='alice@gmail.com')
        movie = movie_factory(tmdb_id=19542, title='The Red Shoes')
        review = review_factory(user=user, movie=movie, review_text='Her EYES. Her EYES', rating=10)
        with pytest.raises(IntegrityError):
            review_factory(user=user, movie=movie, review_text='Damn!', rating=10)

    def test_created_updated_at_auto_set(self, user_factory, movie_factory, review_factory):
        user = user_factory(username='bob', email='bob@mail.com')
        movie = movie_factory(tmdb_id=999, title='Home Alone')
        review = review_factory(user=user, movie=movie, review_text='My childhood fantasy!', rating=8)
        review.review_text = 'The name is McCallister, Kevin McCallister.'
        review.rating = 9
        review.save()
        review.refresh_from_db()
        assert review.created_at is not None
        assert review.updated_at >= review.created_at

    def test_cascade_delete_on_user_delete(self, user_factory, movie_factory, review_factory):
        from reviews.models import Review
        user = user_factory(username='alice')
        movie = movie_factory(tmdb_id=999)
        review = review_factory(user=user, movie=movie)
        user.delete()
        assert not Review.objects.filter(movie=movie).exists()

    def test_cascade_delete_on_movie_delete(self, user_factory, movie_factory, review_factory):
        from reviews.models import Review
        user = user_factory(username='alice')
        movie = movie_factory(tmdb_id=999)
        review = review_factory(user=user, movie=movie)
        movie.delete()
        assert not Review.objects.filter(user=user).exists()
        


"""
ReviewLike model
"""
@pytest.mark.django_db
class TestReviewLikeModel:

    def test_unique_user_review_like_constraint(self, user_factory, movie_factory, review_factory):
        from reviews.models import ReviewLike
        user = user_factory(username='charlie')
        movie = movie_factory(tmdb_id=111)
        review = review_factory(user=user, movie=movie)
        ReviewLike.objects.create(user=user, review=review)
        with pytest.raises(IntegrityError):
            ReviewLike.objects.create(user=user, review=review)


        
"""
ReviewComment model
"""
@pytest.mark.django_db
class TestReviewCommentModel:

    def test_comment_creation(self, user_factory, movie_factory, review_factory):
        from reviews.models import ReviewComment
        user = user_factory(username='charlie')
        movie = movie_factory(tmdb_id=111, title='Interstellar')
        review = review_factory(user=user, movie=movie, review_text='Wow!')
        comment = ReviewComment.objects.create(
            user=user,
            review=review,
            comment_text='I am commenting on this review'
        )
        assert comment.user.username == 'charlie'
        assert comment.review.movie.title == 'Interstellar'
        assert comment.review.review_text == 'Wow!'
        assert comment.comment_text == 'I am commenting on this review'
        assert comment.created_at is not None