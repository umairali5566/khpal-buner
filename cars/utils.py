"""
Utility functions for the cars app
"""
from django.db.models import Q
from cars.models import Car


def get_featured_cars(limit=6):
    """Get featured cars that are not sold"""
    return Car.objects.visible_to_public().filter(is_featured=True)[:limit]


def get_latest_cars(limit=8):
    """Get latest cars that are not sold"""
    return Car.objects.visible_to_public().order_by('-created_at')[:limit]


def search_cars(query, filters=None):
    """
    Search cars by query and optional filters
    
    Args:
        query (str): Search query
        filters (dict): Additional filters
        
    Returns:
        QuerySet: Filtered cars
    """
    cars = Car.objects.visible_to_public()
    
    if query:
        cars = cars.filter(
            Q(brand__icontains=query) |
            Q(model__icontains=query) |
            Q(description__icontains=query) |
            Q(color__icontains=query)
        )
    
    if filters:
        if 'city' in filters and filters['city']:
            cars = cars.filter(city=filters['city'])
        if 'min_price' in filters and filters['min_price']:
            cars = cars.filter(price__gte=filters['min_price'])
        if 'max_price' in filters and filters['max_price']:
            cars = cars.filter(price__lte=filters['max_price'])
        if 'fuel_type' in filters and filters['fuel_type']:
            cars = cars.filter(fuel_type=filters['fuel_type'])
        if 'transmission' in filters and filters['transmission']:
            cars = cars.filter(transmission=filters['transmission'])
        if 'year' in filters and filters['year']:
            cars = cars.filter(year=filters['year'])
    
    return cars
