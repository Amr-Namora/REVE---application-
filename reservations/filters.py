import django_filters
from django.db.models import Q, F
from .models import RealEstate

class RealEstateFilter(django_filters.FilterSet):
    id = django_filters.CharFilter(lookup_expr='iexact')
    city = django_filters.CharFilter(lookup_expr='iexact')
    region = django_filters.filters.CharFilter(field_name='town', lookup_expr='icontains')
    type = django_filters.CharFilter(lookup_expr='iexact')
    minprice = django_filters.filters.NumberFilter(method='filter_minprice')
    maxprice = django_filters.filters.NumberFilter(method='filter_maxprice')
    search = django_filters.CharFilter(method='filter_search')

    class Meta:
        model = RealEstate
        fields = ['city', 'id', 'region', 'type', 'minprice', 'maxprice', 'search']

    def filter_minprice(self, queryset, name, value):
        return queryset.filter(price__gte=round(float(value) / 1.15, 2))  # Adjusting for price * 2

    def filter_maxprice(self, queryset, name, value):
        return queryset.filter(price__lte=round(float(value) / 1.15, 2))  # Adjusting for price * 2

    def filter_search(self, queryset, name, value):
        return queryset.filter(Q(id__iexact=value) | Q(town__icontains=value) | Q(city__icontains=value))
