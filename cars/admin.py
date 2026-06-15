from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from cars.models import (
    Car,
    CarClickAnalytics,
    CarImage,
    CarSearch,
    CarView,
    City,
    DealerProfile,
    Inquiry,
)

@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']
    search_fields = ['name']

class CarImageInline(admin.TabularInline):
    model = CarImage
    extra = 1

@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = ['brand', 'model', 'year', 'price', 'dealer', 'is_sold', 'sold_at', 'is_featured', 'created_at']
    list_filter = ['is_sold', 'is_featured', 'fuel_type', 'transmission', 'year', 'city', 'sold_at']
    search_fields = ['brand', 'model', 'color', 'dealer__shop_name']
    inlines = [CarImageInline]
    list_editable = ['is_sold', 'is_featured']

@admin.register(CarImage)
class CarImageAdmin(admin.ModelAdmin):
    list_display = ['car', 'is_primary', 'created_at']

@admin.register(Inquiry)
class InquiryAdmin(admin.ModelAdmin):
    list_display = ['name', 'phone', 'car', 'is_read', 'created_at']
    list_filter = ['is_read', 'created_at']
    search_fields = ['name', 'phone', 'car__brand', 'car__model']


@admin.register(CarView)
class CarViewAdmin(admin.ModelAdmin):
    list_display = ['car', 'visitor_ip', 'viewed_at']
    list_filter = ['viewed_at']
    search_fields = ['car__brand', 'car__model', 'visitor_ip']
    readonly_fields = ['car', 'visitor_ip', 'viewed_at']


@admin.register(CarSearch)
class CarSearchAdmin(admin.ModelAdmin):
    list_display = ['search_keyword', 'matched_car', 'searched_at']
    list_filter = ['searched_at']
    search_fields = ['search_keyword', 'matched_car__brand', 'matched_car__model']
    readonly_fields = ['search_keyword', 'matched_car', 'searched_at']


@admin.register(CarClickAnalytics)
class CarClickAnalyticsAdmin(admin.ModelAdmin):
    list_display = ['car', 'click_type', 'created_at']
    list_filter = ['click_type', 'created_at']
    search_fields = ['car__brand', 'car__model']
    readonly_fields = ['car', 'click_type', 'created_at']

@admin.register(DealerProfile)
class DealerProfileAdmin(admin.ModelAdmin):
    list_display = ['shop_name', 'owner_name', 'phone', 'city', 'is_suspended', 'created_at']
    list_filter = ['is_suspended', 'city', 'created_at']
    search_fields = ['shop_name', 'owner_name', 'phone']
    list_editable = ['is_suspended']

class DealerProfileInline(admin.StackedInline):
    model = DealerProfile
    can_delete = False
    verbose_name_plural = 'Dealer Profile'

class CustomUserAdmin(UserAdmin):
    inlines = [DealerProfileInline]
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_staff', 'get_dealer_status']
    
    def get_dealer_status(self, obj):
        profile = getattr(obj, 'dealer_profile', None)
        if profile:
            return f"Dealer ({'Suspended' if profile.is_suspended else 'Active'})"
        return "Admin"
    get_dealer_status.short_description = 'Role'

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

# Customize admin site appearance
admin.site.site_header = "Khpal Buner Administration"
admin.site.site_title = "Khpal Buner Admin"
admin.site.index_title = "Welcome to Khpal Buner Admin Panel"
