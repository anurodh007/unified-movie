"""
Similar to urls.py but 'silk' is excluded
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

urlpatterns = [
    path('admin/', admin.site.urls),

    # Session Authentication Endpoint
    path('api-auth/', include('rest_framework.urls')),

    # Authentication urls
    path('api/auth/', include('users.auth_urls')),

    # Users urls
    path('api/users/', include('users.urls')),

    # Movies urls
    path('api/movies/', include('movies.urls')),

    # Watchlist urls
    path('api/watchlist/', include('watchlist.urls')),

    # Recommendation urls
    path('api/recommendations/', include('recommendations.urls')),
]


# Serve static files
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


# Drf-spectacular
urlpatterns += [
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]