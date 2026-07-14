"""
API Tests for Reviews, Comments, Likes

Endpoints under test:

GET/POST                /api/movies/<int:tmdb_id>/reviews/
GET/PUT/PATCH/DELETE    /api/movies/<int:tmdb_id>/reviews/<int:review_id>/

GET/POST                /api/movies/<int:tmdb_id>/reviews/<int:review_id>/comments/
GET/DELETE    /api/movies/<int:tmdb_id>/reviews/<int:review_id>/comments/<int:comment_id>/

GET/POST/DELETE         /api/movies/<int:tmdb_id>/reviews/<int:review_id>/likes/
"""

import pytest
from rest_framework import status
from reviews.models import ReviewComment, ReviewLike
from watchlist.models import Watchlist

# URL Helpers
def reviews_list_url(tmdb_id):
    return f'/api/movies/{tmdb_id}/reviews/'

def review_detail_url(tmdb_id, review_id):
    return f'/api/movies/{tmdb_id}/reviews/{review_id}/'

def comments_url(tmdb_id, review_id):
    return f'/api/movies/{tmdb_id}/reviews/{review_id}/comments/'

def comment_detail_url(tmdb_id, review_id, comment_id):
    return f'/api/movies/{tmdb_id}/reviews/{review_id}/comments/{comment_id}/'

def likes_url(tmdb_id, review_id):
    return f'/api/movies/{tmdb_id}/reviews/{review_id}/likes/'



"""
Review List API
"""
@pytest.mark.django_db
class TestReviewListAPI:

    def test_anonymous_user_can_list_reviews(self, api_client, review_factory, user, movie):
        review_factory(user=user, movie=movie, review_text='Test Review', rating=7)
        response = api_client.get(reviews_list_url(movie.tmdb_id))
        assert response.status_code == status.HTTP_200_OK
        results = response.data['results']
        assert results[0]['rating'] == 7

    def test_reviews_list_filtered_by_movie(self, api_client, review_factory, user, movie_factory):
        m1 = movie_factory(tmdb_id=111, title='Movie')
        m2 = movie_factory(tmdb_id=999, title='Other Movie')
        review_factory(user=user, movie=m1)
        review_factory(user=user, movie=m2)
        response = api_client.get(reviews_list_url(m1.tmdb_id))
        titles = {r['movie'] for r in response.data['results']}
        assert 'Other Movie' not in titles

    def test_authenticated_user_can_create_review(self, auth_client, movie):
        data = {'review_text': 'Test Review', 'rating': 8}
        response = auth_client.post(reviews_list_url(movie.tmdb_id), data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['rating'] == 8

    def test_review_creation_removes_from_watchlist(self, auth_client, user, movie, watchlist_factory):
        watchlist_factory(user=user, movie=movie)
        assert Watchlist.objects.filter(user=user, movie=movie).exists()
        data = {'review_text': 'Nice film!', 'rating': 8}
        auth_client.post(reviews_list_url(movie.tmdb_id), data, format='json')
        assert not Watchlist.objects.filter(user=user, movie=movie).exists()

    def test_duplicate_review_returns_400(self, auth_client, user, movie, review_factory):
        review_factory(user=user, movie=movie)
        response = auth_client.post(reviews_list_url(movie.tmdb_id), {'review_text': 'Test', 'rating': 7}, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_rating_below_1_is_invalid(self, auth_client, movie):
        data = {'review_text': 'Too Low', 'rating': 0}
        response = auth_client.post(reviews_list_url(movie.tmdb_id), data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_rating_above_10_is_invalid(self, auth_client, movie):
        data = {'review_text': 'Too High', 'rating': 11}
        response = auth_client.post(reviews_list_url(movie.tmdb_id), data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_rating_at_boundary_1_is_valid(self, auth_client, movie):
        data = {'review_text': 'Minimum Rating', 'rating': 1}
        response = auth_client.post(reviews_list_url(movie.tmdb_id), data, format='json')
        assert response.status_code == status.HTTP_201_CREATED

    def test_rating_at_boundary_10_is_valid(self, auth_client, movie):
        data = {'review_text': 'Maximum Rating', 'rating': 10}
        response = auth_client.post(reviews_list_url(movie.tmdb_id), data, format='json')
        assert response.status_code == status.HTTP_201_CREATED

    def test_non_integer_rating_is_invalid(self, auth_client, movie):
        data = {'review_text': 'Float Rating', 'rating': 7.5}
        response = auth_client.post(reviews_list_url(movie.tmdb_id), data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_missing_review_text_returns_400(self,auth_client, movie):
        data = {'rating': 10}
        response = auth_client.post(reviews_list_url(movie.tmdb_id), data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST


    
"""
Review Detail API
"""
@pytest.mark.django_db
class TestReviewDetailAPI:

    def test_retrieve_review(self, api_client, movie, review):
        response = api_client.get(review_detail_url(movie.tmdb_id, review.pk))
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == review.pk

    def test_owner_can_update_review(self, auth_client, movie, review):
        data = {'review_text': 'Updated Text', 'rating': 7}
        response = auth_client.put(review_detail_url(movie.tmdb_id, review.pk), data, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['review_text'] == 'Updated Text'

    def test_owner_can_delete_review(self, auth_client, movie, review):
        response = auth_client.delete(review_detail_url(movie.tmdb_id, review.pk))
        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_non_owner_cannot_update_review(self, auth_client, other_user, movie, review_factory):
        review = review_factory(user=other_user, movie=movie, review_text='Other Users Review', rating=7)
        response = auth_client.patch(review_detail_url(movie.tmdb_id, review.pk), {'review_text': 'Users Review'}, format='json')
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_non_owner_cannot_delete_review(self, auth_client, other_user, movie, review_factory):
        review = review_factory(user=other_user, movie=movie, review_text='Other Users Review', rating=7)
        response = auth_client.delete(review_detail_url(movie.tmdb_id, review.pk))
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_nonexistent_review_returns_404(self, api_client, movie):
        response = api_client.get(review_detail_url(movie.tmdb_id, 999))
        assert response.status_code == status.HTTP_404_NOT_FOUND



"""
Comments API
"""
@pytest.mark.django_db
class TestCommentsAPI:

    def test_anonymous_can_list_comments(self, api_client, user, movie, review):
        ReviewComment.objects.create(user=user, review=review, comment_text='First Comment')
        response = api_client.get(comments_url(movie.tmdb_id, review.pk))
        assert response.status_code == status.HTTP_200_OK
        results = response.data['results']
        assert results[0]['comment_text'] == 'First Comment'

    def test_authenticated_user_can_create_comment(self, auth_client, movie, review):
        data = {'comment_text': 'Haha, Nice Review.'}
        response = auth_client.post(comments_url(movie.tmdb_id, review.pk), data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['comment_text'] == 'Haha, Nice Review.'

    def test_anonymous_user_cannot_create_comment(self, api_client, movie, review):
        data = {'comment_text': 'Unknown User'}
        response = api_client.post(comments_url(movie.tmdb_id, review.pk), data, format='json')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_comment_owner_can_delete_comment(self, auth_client, user, movie, review):
        comment = ReviewComment.objects.create(user=user, review=review, comment_text='Owner Comment')
        response = auth_client.delete(comment_detail_url(movie.tmdb_id, review.pk, comment.pk))
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not ReviewComment.objects.filter(user=user, review=review).exists()

    def test_review_owner_can_delete_comment(self, auth_client, user, other_user, movie, review_factory):
        review = review_factory(user=user, movie=movie, review_text='Users Review', rating=8)
        comment = ReviewComment.objects.create(user=other_user, review=review, comment_text='Other Users Comment')
        response = auth_client.delete(comment_detail_url(movie.tmdb_id, review.pk, comment.pk))
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not ReviewComment.objects.filter(user=other_user, review=review).exists()

    def test_unrelated_user_cannot_delete_comment(self, other_auth_client, user, movie, review, user_factory):
        third = user_factory(username='third', email='third@mail.com')
        comment = ReviewComment.objects.create(user=third, review=review, comment_text='Third Users Comment')
        response = other_auth_client.delete(comment_detail_url(movie.tmdb_id, review.pk, comment.pk))
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert ReviewComment.objects.filter(user=third, review=review).exists()



"""
Likes API
"""
@pytest.mark.django_db
class TestLikesAPI:

    def test_anonymous_user_can_list_likes(self, api_client, movie, review):
        response = api_client.get(likes_url(movie.tmdb_id, review.pk))
        assert response.status_code == status.HTTP_200_OK

    def test_anonymous_user_cannot_like_review(self, api_client, movie, review):
        response = api_client.post(likes_url(movie.tmdb_id, review.pk))
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_non_owner_can_like_review(self, other_auth_client, other_user, movie, review):
        response = other_auth_client.post(likes_url(movie.tmdb_id, review.pk), {}, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['user'] == other_user.username

    def test_review_owner_cannot_like_review(self, auth_client, movie, review):
        response = auth_client.post(likes_url(movie.tmdb_id, review.pk), {}, format='json')
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_duplicate_likes_not_allowed(self, other_auth_client, other_user, movie, review):
        like = ReviewLike.objects.create(user=other_user, review=review)
        response = other_auth_client.post(likes_url(movie.tmdb_id, review.pk), {}, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_unlike_deletes_like(self, other_auth_client, other_user, movie, review):
        like = ReviewLike.objects.create(user=other_user, review=review)
        assert ReviewLike.objects.filter(user=other_user, review=review).exists()
        response = other_auth_client.delete(likes_url(movie.tmdb_id, review.pk), {}, format='json')
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not ReviewLike.objects.filter(user=other_user, review=review).exists()