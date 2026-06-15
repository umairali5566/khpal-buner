from django.core.management.base import BaseCommand
from cars.models import City


class Command(BaseCommand):
    help = 'Setup initial data for the Khpal Buner application'

    def handle(self, *args, **options):
        # Create default cities
        cities = [
            'Karachi',
            'Lahore',
            'Islamabad',
            'Rawalpindi',
            'Faisalabad',
            'Multan',
            'Peshawar',
            'Quetta',
            'Hyderabad',
            'Sukkur',
        ]

        created_count = 0
        for city_name in cities:
            city, created = City.objects.get_or_create(name=city_name)
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Created city: {city_name}')
                )
            else:
                self.stdout.write(f'✓ City already exists: {city_name}')

        self.stdout.write(
            self.style.SUCCESS(f'\nSuccessfully created {created_count} cities')
        )
