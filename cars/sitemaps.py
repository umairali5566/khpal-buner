from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from cars.models import Car, DealerProfile

class CarSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.9

    def items(self):
        return Car.objects.visible_to_public()

    def lastmod(self, obj):
        return obj.updated_at

class DealerSitemap(Sitemap):
    changefreq = 'monthly'
    priority = 0.8

    def items(self):
        return DealerProfile.objects.filter(is_suspended=False)

    def lastmod(self, obj):
        return obj.updated_at
