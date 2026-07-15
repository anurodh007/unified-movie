"""
Shared fixtures for the recommendation tests
"""

import pytest
import random
from django.contrib.auth import get_user_model
from movies.models import Movie, Genre
from reviews.models import Review

User = get_user_model()


"""
Content-Based Recommendation Fixture
"""
@pytest.fixture
def content_based_dataset(db):
    user = User.objects.create_user(username='test', email='test@mail.com', password='StrongPass123!')
    action = Genre.objects.create(tmdb_id='28', name='Action')
    comedy = Genre.objects.create(tmdb_id='40', name='Comedy')
    drama = Genre.objects.create(tmdb_id='18', name='Drama')

    for i in range(1, 11):
        movie = Movie.objects.create(tmdb_id=i + 100, title=f'Movie {i}')
        movie.genres.add(action, comedy)
    for i in range(1, 11):
        movie = Movie.objects.create(tmdb_id=i + 200, title=f'Movie {i + 10}')
        movie.genres.add(action, drama)
    for i in range(1, 11):
        movie = Movie.objects.create(tmdb_id=i + 300, title=f'Movie {i + 20}')
        movie.genres.add(comedy, drama)

    return {
        'user': user,
    }


"""
Collaborative Recommendation fixture
"""
@pytest.fixture
def collab_dataset(db):
    rng = random.Random(69)

    for i in range(1, 11):
        User.objects.create_user(username=f'test{i}', password='StrongPass123!')
    
    for i in range(1, 11):
        Movie.objects.create(tmdb_id=i + 100, title='Movie {i}')
    for i in range(1, 11):
        Movie.objects.create(tmdb_id=i + 200, title=f'Movie {i + 10}')
    for i in range(1, 11):
        Movie.objects.create(tmdb_id=i + 300, title=f'Movie {i + 20}')

    users = User.objects.all()
    movies = Movie.objects.all()

    for _ in range(100):
        Review.objects.create(
            user=rng.choice(users),
            movie=rng.choice(movies),
            rating=rng.randint(1, 10)
        )
    
    return {
        'users': users,
        'movies': movies
    }