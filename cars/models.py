from datetime import timedelta
import re
from urllib.parse import parse_qs, quote_plus, unquote, urlparse

from django.db import models
from django.db.models import Q
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone

class City(models.Model):
    name = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Cities"
        ordering = ['name']

    def __str__(self):
        return self.name

class DealerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='dealer_profile')
    shop_name = models.CharField(max_length=200)
    owner_name = models.CharField(max_length=100)
    profile_picture = models.ImageField(upload_to='dealers/', blank=True)
    phone = models.CharField(max_length=20)
    whatsapp = models.CharField(max_length=20, blank=True)
    address = models.TextField()
    city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True)
    google_maps_link = models.URLField(blank=True, help_text="Google Maps location link")
    is_suspended = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    must_change_password = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.shop_name

    def get_absolute_url(self):
        return reverse('dealer_detail', kwargs={'pk': self.pk})

    def get_google_maps_embed_url(self):
        link = self.google_maps_link.strip()
        if not link:
            return ''

        parsed_url = urlparse(link)
        query_params = parse_qs(parsed_url.query)

        location_query = ''
        coordinate_match = re.search(r'@(-?\d+(?:\.\d+)?),(-?\d+(?:\.\d+)?)', link)
        data_coordinate_match = re.search(r'!3d(-?\d+(?:\.\d+)?)!4d(-?\d+(?:\.\d+)?)', link)
        if coordinate_match:
            location_query = f'{coordinate_match.group(1)},{coordinate_match.group(2)}'
        elif data_coordinate_match:
            location_query = f'{data_coordinate_match.group(1)},{data_coordinate_match.group(2)}'
        elif query_params.get('q'):
            location_query = query_params['q'][0]
        elif query_params.get('query'):
            location_query = query_params['query'][0]
        elif query_params.get('ll'):
            location_query = query_params['ll'][0]
        elif '/maps/place/' in parsed_url.path:
            place_slug = parsed_url.path.split('/maps/place/', 1)[1].split('/', 1)[0]
            location_query = unquote(place_slug).replace('+', ' ')

        if not location_query:
            city_name = self.city.name if self.city_id and self.city else ''
            location_query = f'{self.address} {city_name}'.strip()

        return f'https://www.google.com/maps?q={quote_plus(location_query)}&output=embed'

class CarQuerySet(models.QuerySet):
    def available(self):
        return self.filter(is_sold=False)

    def visible_to_public(self):
        sold_cutoff = timezone.now() - timedelta(hours=24)
        return self.filter(Q(is_sold=False) | Q(is_sold=True, sold_at__gte=sold_cutoff))


class Car(models.Model):
    FUEL_CHOICES = [
        ('petrol', 'Petrol'),
        ('diesel', 'Diesel'),
        ('cng', 'CNG'),
        ('hybrid', 'Hybrid'),
        ('electric', 'Electric'),
    ]
    
    TRANSMISSION_CHOICES = [
        ('manual', 'Manual'),
        ('automatic', 'Automatic'),
    ]

    dealer = models.ForeignKey(DealerProfile, on_delete=models.CASCADE, related_name='cars')
    brand = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    year = models.PositiveIntegerField()
    color = models.CharField(max_length=50)
    price = models.PositiveIntegerField(help_text="Price in PKR")
    mileage = models.PositiveIntegerField(help_text="Mileage in km")
    fuel_type = models.CharField(max_length=20, choices=FUEL_CHOICES)
    transmission = models.CharField(max_length=20, choices=TRANSMISSION_CHOICES)
    description = models.TextField()
    city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True)
    is_sold = models.BooleanField(default=False)
    sold_at = models.DateTimeField(null=True, blank=True, db_index=True)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = CarQuerySet.as_manager()

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.year} {self.brand} {self.model}"

    def get_absolute_url(self):
        return reverse('car_detail', kwargs={'pk': self.pk})

    def save(self, *args, **kwargs):
        update_fields = kwargs.get('update_fields')
        if self.is_sold and self.sold_at is None:
            self.sold_at = timezone.now()
            if update_fields is not None:
                kwargs['update_fields'] = set(update_fields) | {'sold_at'}
        elif not self.is_sold and self.sold_at is not None:
            self.sold_at = None
            if update_fields is not None:
                kwargs['update_fields'] = set(update_fields) | {'sold_at'}
        super().save(*args, **kwargs)

    def mark_sold(self):
        self.is_sold = True
        self.sold_at = self.sold_at or timezone.now()
        self.save(update_fields=['is_sold', 'sold_at', 'updated_at'])

    def mark_available(self):
        self.is_sold = False
        self.sold_at = None
        self.save(update_fields=['is_sold', 'sold_at', 'updated_at'])

    def is_publicly_visible(self):
        if not self.is_sold:
            return True
        if self.sold_at is None:
            return False
        return self.sold_at >= timezone.now() - timedelta(hours=24)

class CarImage(models.Model):
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='cars/')
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-is_primary', 'created_at']

    def __str__(self):
        return f"Image for {self.car}"

class Inquiry(models.Model):
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='inquiries')
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Inquiry from {self.name} for {self.car}"


class CarView(models.Model):
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='views')
    visitor_ip = models.GenericIPAddressField(null=True, blank=True)
    viewed_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-viewed_at']
        indexes = [
            models.Index(fields=['car', '-viewed_at']),
            models.Index(fields=['visitor_ip', '-viewed_at']),
        ]

    def __str__(self):
        return f"View for {self.car} at {self.viewed_at}"


class CarSearch(models.Model):
    search_keyword = models.CharField(max_length=255, db_index=True)
    matched_car = models.ForeignKey(
        Car,
        on_delete=models.CASCADE,
        related_name='searches',
        null=True,
        blank=True,
    )
    searched_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-searched_at']
        indexes = [
            models.Index(fields=['matched_car', '-searched_at']),
            models.Index(fields=['search_keyword', '-searched_at']),
        ]

    def __str__(self):
        return f"{self.search_keyword} -> {self.matched_car or 'No match'}"


class CarClickAnalytics(models.Model):
    VIEW_DETAILS = 'view_details'
    WHATSAPP = 'whatsapp'
    CALL = 'call'

    CLICK_TYPE_CHOICES = [
        (VIEW_DETAILS, 'View Details'),
        (WHATSAPP, 'WhatsApp'),
        (CALL, 'Call Dealer'),
    ]

    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='clicks')
    click_type = models.CharField(max_length=20, choices=CLICK_TYPE_CHOICES, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['car', 'click_type', '-created_at']),
        ]
        verbose_name_plural = 'Car click analytics'

    def __str__(self):
        return f"{self.get_click_type_display()} for {self.car}"
