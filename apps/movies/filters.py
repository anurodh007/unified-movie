import django_filters
from movies.models import Movie


class MovieFilter(django_filters.FilterSet):
    year = django_filters.NumberFilter(field_name='release_date', lookup_expr='year')
    year_range = django_filters.NumericRangeFilter(field_name='release_date', lookup_expr='year__range')

    genre = django_filters.CharFilter(field_name='genres__name', lookup_expr='icontains')

    class Meta:
        model = Movie
        fields = {
            'runtime': ['lt'],
        }