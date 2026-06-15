from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from cars.sitemaps import CarSitemap, DealerSitemap
from cars import views

sitemaps = {
    'cars': CarSitemap,
    'dealers': DealerSitemap,
}

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('cars/', views.car_list, name='car_list'),
    path('cars/<int:pk>/', views.car_detail, name='car_detail'),
    path('cars/<int:pk>/track-click/', views.car_click_analytics, name='car_click_analytics'),
    path('dealers/', views.dealer_list, name='dealer_list'),
    path('dealer/<int:pk>/', views.dealer_detail, name='dealer_detail'),
    path('contact/', views.contact, name='contact'),
    path('dashboard/', views.dealer_dashboard, name='dealer_dashboard'),
    path('car/add/', views.car_create, name='car_add'),
    path('car/<int:pk>/edit/', views.car_edit, name='car_edit'),
    path('car/<int:pk>/delete/', views.car_delete, name='car_delete'),
    path('car/<int:pk>/sold/', views.car_mark_sold, name='car_mark_sold'),
    path('car/<int:pk>/available/', views.car_mark_available, name='car_mark_available'),
    path('profile/', views.dealer_profile_view, name='dealer_profile'),
    path('password-change/', views.password_change_view, name='password_change'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='sitemap'),
    path('robots.txt', views.robots_txt, name='robots_txt'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = 'cars.views.handler404'
handler500 = 'cars.views.handler500'
