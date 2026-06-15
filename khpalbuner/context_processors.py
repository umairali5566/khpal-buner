"""
Context processors for template global variables
"""
from cars.models import City


def global_context(request):
    """
    Add global context variables available to all templates
    """
    return {
        'all_cities': City.objects.all(),
        'site_name': 'Khpal Buner',
    }
