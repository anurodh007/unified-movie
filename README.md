# Unified Movie Platform (UMP) API

A unified social cataloging, review, and personalization API for movies. Built with **Django REST Framework (DRF)**, the platform integrates with The Movie Database (TMDB) API to fetch metadata, watch providers, and trending movies, and caches data using a high-performance Redis layer. Additionally, it implements a dual recommendation engine that computes personalized recommendations using content-based and user-to-user collaborative filtering.

---

## Features

- **User Accounts & Profiles**: JWT-based authentication (login, registration, token refresh). Profiles include customizable bios and profile picture uploads, which are auto-resized to a standard 300x300px format.
- **Movies Catalog**: Automatically fetches detailed movie metadata (synopsis, genre classification, release date, runtime, poster/backdrop images, popularity statistics) from the TMDB API and mirrors it locally.
- **Dynamic Caching**: All high-load operations—such as movie searches, trending queries, streaming provider updates, and recommendation vectors—are cached in Redis to minimize network latency.
- **Interactive Watchlist**: Allows users to save movies they plan to watch. To keep the workflow natural, movies are automatically removed from the watchlist as soon as a user submits a review.
- **Social & Review System**: Users can rate movies (on a scale from 1 to 10), write reviews, comment on reviews, and like reviews. Constraints prevent users from writing multiple reviews for the same movie or liking their own reviews.
- **Automated Movie Statistics**: Review additions, updates, or deletions trigger real-time, atomic database recalculations of the movie's global vote count and average rating.
- **Watch Providers (Streaming Platforms)**: Dynamically checks where a movie is currently streaming (rent, flatrate subscriptions, or buy options) in the United States using TMDB's Watch Providers database.
- **Advanced Filtering**: Search and narrow down movies by release year, year range, maximum runtime, or multiple matching genres (e.g., `Action,Adventure`).
- **Adaptive Recommendation System**: Routes users to a content-based recommendation model or a user-based collaborative filtering model based on user activity levels.
- **Interactive API Documentation & Profiling**: Fully integrated OpenAPI 3.0 schema generation served via Swagger UI and ReDoc. Internal request profiling is enabled via Django Silk.

---

## Tech Stack

- **Framework**: Django 6.0.3 & Django REST Framework (DRF) 3.16.1
- **Database**: MySQL (via `mysqlclient` 2.2.8)
- **Caching & Session Storage**: Redis (via `django-redis` 6.0.0 & `redis` 7.3.0)
- **Authentication**: JWT (JSON Web Tokens via `djangorestframework_simplejwt` 5.5.1)
- **Image Processing**: Pillow 12.1.1 (profile image resizing and validation)
- **Mathematical Computations**: NumPy 2.5.1 (vector-based recommendation scoring)
- **Query Filtering**: Django Filter 25.2
- **Documentation**: DRF Spectacular 0.29.0 (Swagger UI / ReDoc)
- **Profiling**: Django Silk 5.5.0

---

## Project Architecture

The project is structured following clean coding guidelines with segregated responsibility:
- **`apps/`**: Self-contained Django applications.
  - **`users`**: Custom user models, JWT authentication endpoints, profile retrieval, and public vs. private serializers.
  - **`movies`**: Local database schemas for movies, genres, and streaming platforms, TMDB API services, and custom filter configurations.
  - **`reviews`**: Models for movie reviews, comments, and review likes. Includes custom permission classes (e.g., preventing users from liking their own reviews) and signals to recalculate movie stats.
  - **`watchlist`**: Simple models and operations to manage user watchlist bookmarks.
  - **`recommendations`**: Dual recommendation services and algorithms (math/matrix logic for matching user tastes).
- **`core/`**: Shared components, including custom global permissions and OpenAPI schemas.
- **`config/`**: Global settings, environment definitions, and root URL configurations.
- **Caching Layer**: Service layers fetch from TMDB, write to the database, and write to Redis. Database queries leverage `.select_related()` and `.prefetch_related()` to avoid N+1 query bottlenecks.
- **Signals System**: Fully decoupled event listener signals automate data recalculation and cache invalidation.

---

## Installation

### Prerequisites
- Python 3.10+
- MySQL Server
- Redis Server

### Setup Steps
1. **Clone the Repository**
   ```bash
   git clone https://github.com/anurodh007/unified-movie.git
   cd ump
   ```

2. **Create a Virtual Environment**
   ```bash
   python -m venv venv
   # On Windows:
   .\venv\Scripts\activate
   # On Unix/macOS:
   source venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Setup Database Configuration**
   Copy the example database configuration file:
   ```bash
   copy db.cnf.example db.cnf
   ```
   Edit the newly created `db.cnf` to provide your MySQL database credentials:
   ```ini
   [client]
   database = your_database_name
   user = your_mysql_username
   password = your_mysql_password
   host = localhost
   port = 3306
   default-character-set = utf8mb4
   ```

5. **Setup Environment Variables**
   Copy the example environment configuration file:
   ```bash
   copy .env.example .env
   ```
   Edit the `.env` file and replace the placeholders:
   ```env
   DJANGO_SETTINGS_MODULE=config.settings
   DEBUG=True
   SECRET_KEY=your_django_secret_key_here
   API_KEY=your_tmdb_api_key_here
   TMDB_BASE_URL=https://api.themoviedb.org/3
   TMDB_IMAGE_BASE_URL=https://image.tmdb.org/t/p
   ```

---

## Running the Server

1. **Verify Services**: Ensure MySQL and Redis servers are running locally.
2. **Apply Migrations**:
   ```bash
   python manage.py migrate
   ```
3. **Synchronize TMDB Metadata**: Run the management commands to populate the local lookup database with genres and platforms:
   ```bash
   # Sync movie genres from TMDB
   python manage.py sync_genres
   
   # Sync streaming platforms metadata from TMDB
   python manage.py sync_platforms
   ```
4. **Seed Database Movies**: Populate initial movie records from TMDB's popular, top-rated, and weekly trending lists:
   ```bash
   python manage.py seed_movies
   ```
5. **Create a Superuser** (Optional, for admin panel access):
   ```bash
   python manage.py createsuperuser
   ```
6. **Start the Django Development Server**:
   ```bash
   python manage.py runserver
   ```
   The API will be available at `http://127.0.0.1:8000/`.

---

## Environment Variables

| Variable | Description | Default / Example |
|---|---|---|
| `DJANGO_SETTINGS_MODULE` | The active Django configuration file module. | `config.settings` |
| `DEBUG` | Enable or disable Django debug mode. | `True` |
| `SECRET_KEY` | Secret key used for cryptographic signing. | *Generate a secure key* |
| `API_KEY` | Personal API Key for The Movie Database (TMDB). | *Required for TMDB requests* |
| `TMDB_BASE_URL` | The endpoint url for the TMDB version 3 API. | `https://api.themoviedb.org/3` |
| `TMDB_IMAGE_BASE_URL` | The base URL for fetching movie posters and backdrops. | `https://image.tmdb.org/t/p` |

---

## API Overview

### Authentication
| Endpoint | Method | Description | Auth Required |
|---|---|---|---|
| `/api/auth/register/` | `POST` | Register a new user account. | No |
| `/api/auth/login/` | `POST` | Submit credentials to receive JWT Access and Refresh Tokens. | No |
| `/api/auth/refresh/` | `POST` | Submit a Refresh Token to receive a new Access Token. | No |

### User Profiles
| Endpoint | Method | Description | Auth Required |
|---|---|---|---|
| `/api/users/<username>/` | `GET` | Retrieve user profile details. | No (Owner sees email field) |
| `/api/users/<username>/` | `PUT` / `PATCH` | Update profile information (first/last name, bio, profile image). | Yes (Owner only) |
| `/api/users/<username>/watchlist/` | `GET` | List a user's bookmarked watchlist. | No |
| `/api/users/<username>/reviews/` | `GET` | List all movie reviews authored by a user. | No |
| `/api/users/<username>/comments/` | `GET` | List all review comments authored by a user. | No |
| `/api/users/<username>/likes/` | `GET` | List all reviews liked by a user. | No |

### Movies & Catalogs
| Endpoint | Method | Description | Auth Required |
|---|---|---|---|
| `/api/movies/` | `GET` | List movies (ordered by popularity). Query param `?search=<query>` triggers search. | No |
| `/api/movies/<tmdb_id>/` | `GET` | Retrieve detail of a movie (automatically seeds from TMDB if missing). | No |
| `/api/movies/genres/` | `GET` | List all cached genres. | No |
| `/api/movies/platforms/` | `GET` | List all cached streaming platforms. | No |
| `/api/movies/trending/` | `GET` | List daily trending movies (paginated). | No |
| `/api/movies/<tmdb_id>/streaming/` | `GET` | List the US watch providers (rent/flatrate/buy) for a movie. | No |

### Watchlists
| Endpoint | Method | Description | Auth Required |
|---|---|---|---|
| `/api/watchlist/` | `GET` | List the authenticated user's watchlist (ordered by date bookmarked). | Yes |
| `/api/watchlist/` | `POST` | Add a movie to the watchlist (expects `tmdb_id`). | Yes |
| `/api/watchlist/<tmdb_id>/` | `DELETE` | Remove a movie from the watchlist. | Yes |

### Reviews, Comments & Social Interactions
| Endpoint | Method | Description | Auth Required |
|---|---|---|---|
| `/api/movies/<tmdb_id>/reviews/` | `GET` | List all reviews for a movie. | No |
| `/api/movies/<tmdb_id>/reviews/` | `POST` | Create a review + rating (1-10) for a movie (removes it from watchlist). | Yes |
| `/api/movies/<tmdb_id>/reviews/<review_id>/` | `GET` | Retrieve specific review details. | No |
| `/api/movies/<tmdb_id>/reviews/<review_id>/` | `PUT` / `PATCH` | Update review text or rating. | Yes (Owner only) |
| `/api/movies/<tmdb_id>/reviews/<review_id>/` | `DELETE` | Delete review. | Yes (Owner only) |
| `/api/movies/<tmdb_id>/reviews/<review_id>/comments/` | `GET` | List all comments on a review. | No |
| `/api/movies/<tmdb_id>/reviews/<review_id>/comments/` | `POST` | Post a comment on a review. | Yes |
| `/api/movies/<tmdb_id>/reviews/<review_id>/comments/<comment_id>/` | `GET` | Retrieve comment details. | No |
| `/api/movies/<tmdb_id>/reviews/<review_id>/comments/<comment_id>/` | `DELETE` | Delete comment. | Yes (Comment or Review Owner) |
| `/api/movies/<tmdb_id>/reviews/<review_id>/likes/` | `GET` | List users who liked the review. | No |
| `/api/movies/<tmdb_id>/reviews/<review_id>/likes/` | `POST` | Toggle like on a review. | Yes (Review Owner cannot like) |
| `/api/movies/<tmdb_id>/reviews/<review_id>/likes/` | `DELETE` | Unlike a review. | Yes |

### Personalized Recommendations
| Endpoint | Method | Description | Auth Required |
|---|---|---|---|
| `/api/recommendations/` | `GET` | Retrieve personalized recommendations (paginated). | Yes |

### Developer Tools & Specs
| Endpoint | Method | Description | Auth Required |
|---|---|---|---|
| `/api/schema/` | `GET` | Generate OpenAPI 3.0 schema file. | No |
| `/api/schema/swagger-ui/` | `GET` | Swagger UI documentation console. | No |
| `/api/schema/redoc/` | `GET` | ReDoc API documentation browser. | No |
| `/silk/` | `GET` | Django Silk profiling dashboard. | No |

---

## Recommendation System

The platform features an intelligent, automated routing system that balances user profiling data with collaborative network similarities.

```
                  Personalized Request
                           │
                  [ Check Review Count ]
                           │
             ┌─────────────┴─────────────┐
             ▼                           ▼
      Count <= 5                  Count > 5
    [Content-Based]            [Collaborative]
             │                           │
             │                    ┌──────┴──────┐
             │                    ▼             ▼
             │                Has Results?   No Results
             │                   (KNN)           │
             │                     │             │
             │                     ▼             ▼
             └──────────────► [ Return List ] ◄──┘
```

### 1. Strategy Selector
When a user requests recommendations:
1. The system queries their total number of authored reviews.
2. If the user has **5 or fewer reviews**, it uses **Content-Based Filtering** to avoid the cold-start problem.
3. If the user has **more than 5 reviews**, it triggers **Collaborative Filtering**. If this algorithm yields empty results, it fallback-routes back to Content-Based filtering.

### 2. Content-Based Filtering
This model matches the specific genre preferences of an individual to candidate movies:
- **Master Genre Mapping**: Builds a master list of all genres sorted alphabetically.
- **Movie Vectors**: Converts each movie into a binary NumPy vector, representing the presence ($1$) or absence ($0$) of each master genre:
  $$\vec{M} \in \{0, 1\}^{N}$$
- **User Vector**: Computed as the mathematical mean of movie vectors for all movies rated $7$ or higher by the user:
  $$\vec{U} = \frac{1}{|R_{7+}|} \sum_{m \in R_{7+}} \vec{M}_m$$
- **Cosine Similarity**: Measures the angle of similarity between the user preference vector and candidate movies:
  $$\text{Score}(u, m) = \frac{\vec{U} \cdot \vec{M}_m}{\|\vec{U}\| \|\vec{M}_m\|}$$
- **Filtering**: Sorts candidate movies by similarity. Before returning results, the system excludes movies the user has already reviewed or placed in their watchlist.

### 3. Collaborative Filtering (User-User KNN)
This model maps patterns across users to predict what ratings a user would give to unrated movies:
- **User-Movie Rating Matrix**: Builds a matrix where rows are users, columns are movies, and values represent submitted ratings. The matrix is cached in Redis for 12 hours.
- **User Similarity**: Computes cosine similarity between the current user's rating vector and all other users' rating vectors in the matrix:
  $$\text{Sim}(u, v) = \frac{\vec{R}_u \cdot \vec{R}_v}{\|\vec{R}_u\| \|\vec{R}_v\|}$$
- **Rating Prediction**: Identifies the $K$ nearest neighbors ($k=3$ by default) who have rated the candidate movie $m$. It predicts the rating using a similarity-weighted average:
  $$\text{Pred}(u, m) = \frac{\sum_{v \in KNN(u)} \text{Sim}(u, v) \times \text{Rating}(v, m)}{\sum_{v \in KNN(u)} \text{Sim}(u, v)}$$
- **Ranking**: Movies are ranked in descending order of predicted rating.

### 4. Cache Invalidation
Decoupled signals listen for reviews creation, modification, or deletion. When triggered, the signal invalidates:
- The user's genre vector (`user_vector_<id>`).
- The user's content-based similarity scores (`similarity_scores_<id>`).
- The user's collaborative similarity index (`user_similarity_<id>`).
- The user's predicted rating lists (`predicted_ratings_<id>`).
- The global rating matrix (`user_movie_matrix`).

---

## Project Structure

```
ump/
│
├── apps/
│   ├── movies/
│   │   ├── management/commands/  # CLI scripts for seeding and syncing metadata
│   │   ├── serializers/          # Genre, Platform, Movie serializers & TMDBImageField
│   │   ├── services/             # TMDB HTTP Client and cache wrapper
│   │   ├── filters.py            # Custom movie search & filter parameters
│   │   ├── models.py             # Genre, Movie, StreamingPlatform schemas
│   │   ├── urls.py               # Movies and watch provider routes
│   │   └── views.py              # Catalog, Search, and watch provider views
│   │
│   ├── recommendations/
│   │   ├── algorithms/
│   │   │   ├── collaborative/    # Matrix, similarity, prediction, and ranking logic
│   │   │   └── content_based/    # Vector construction, similarity, and ranking logic
│   │   ├── services/             # Strategy selector orchestrator
│   │   ├── serializers.py        # Custom RecommendationSerializer
│   │   ├── signals.py            # Cache invalidation listeners
│   │   ├── urls.py               # Recommendations endpoint mappings
│   │   └── views.py              # Personalized recommendations API handler
│   │
│   ├── reviews/
│   │   ├── serializers/          # Review, Comment, and Like serializers
│   │   ├── models.py             # Review, ReviewLike, ReviewComment schemas
│   │   ├── permissions.py        # Social boundary check permissions
│   │   ├── signals.py            # Signals to recalculate movie rating statistics
│   │   ├── urls.py               # Movie review system routes
│   │   └── views.py              # Views for reviews, comments, and likes
│   │
│   ├── users/
│   │   ├── serializers/          # Registration and public/owner profile serializers
│   │   ├── auth_urls.py          # User registration and JWT login routes
│   │   ├── models.py             # Custom user model with profile image resizing
│   │   ├── permissions.py        # Owner profile access validations
│   │   ├── urls.py               # Social activity & user profile views
│   │   └── views.py              # Profile views
│   │
│   └── watchlist/
│       ├── models.py             # Watchlist bookmarks schema
│       ├── serializers.py        # Watchlist serializers (maps tmdb_id)
│       ├── urls.py               # Add/Remove from watchlist endpoints
│       └── views.py              # Watchlist views
│
├── config/
│   ├── settings.py               # Django configuration (Database, JWT, Caches, Apps)
│   ├── urls.py                   # Master URL routing table
│   └── env.py                    # Environment loader configuration
│
├── core/
│   ├── permissions.py            # Global IsOwnerOrReadOnly class
│   └── schema.py                 # Custom openapi schema generators
│
├── requirements.txt              # Project packages list
├── manage.py                     # Django management script
├── api.http                      # Sample requests testing file
└── README.md                     # Project documentation (this file)
```

---

## Contributors

- **Anurodh** - Core Developer / Architecture Designer

---
