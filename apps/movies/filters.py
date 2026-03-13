import django_filters
from movies.models import Movie


class MovieFilter(django_filters.FilterSet):
    year = django_filters.NumberFilter(field_name='release_date', lookup_expr='year')
    year_range = django_filters.NumericRangeFilter(field_name='release_date', lookup_expr='year__range')

    genres = django_filters.CharFilter(method='filter_by_all_genres')

    class Meta:
        model = Movie
        fields = {
            'runtime': ['lt'],
        }

    def filter_by_all_genres(self, queryset, name, value):
        genres_list = [g.strip() for g in value.split(',') if g.strip()]
        for genre in genres_list:
            queryset = queryset.filter(genres__name__iexact=genre)
        return queryset.distinct()