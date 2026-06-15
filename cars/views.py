from datetime import timedelta

from django.shortcuts import render, get_object_or_404, redirect
from django.http import Http404, JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.db.models import Count, Max, Q
from django.utils import timezone
from django.views.decorators.http import require_POST
from cars.models import (
    Car,
    CarClickAnalytics,
    CarImage,
    CarSearch,
    CarView,
    Inquiry,
    City,
    DealerProfile,
)
from cars.forms import CarForm, InquiryForm, SearchForm, PasswordChangeForm

HIGH_DEMAND_SEARCH_THRESHOLD = 50


def get_visitor_ip(request):
    return request.META.get('REMOTE_ADDR') or None


def get_car_name(car):
    return f"{car.year} {car.brand} {car.model}"


def get_search_keyword(request, search_form):
    parts = []
    hero_query = request.GET.get('q', '').strip()
    if hero_query:
        parts.append(hero_query)

    if search_form.is_valid():
        label_map = {
            'brand': 'Brand',
            'model': 'Model',
            'year': 'Year',
            'color': 'Color',
            'city': 'City',
            'min_price': 'Min price',
            'max_price': 'Max price',
            'fuel_type': 'Fuel',
            'transmission': 'Transmission',
        }
        for field_name, label in label_map.items():
            value = search_form.cleaned_data.get(field_name)
            if value:
                parts.append(f"{label}: {value}")

    return ', '.join(parts)[:255]


def record_car_search(search_keyword, matched_cars):
    if not search_keyword:
        return

    matched_car_ids = list(matched_cars.values_list('id', flat=True))
    if matched_car_ids:
        CarSearch.objects.bulk_create(
            [
                CarSearch(search_keyword=search_keyword, matched_car_id=car_id)
                for car_id in matched_car_ids
            ],
            batch_size=500,
        )
        return

    CarSearch.objects.create(search_keyword=search_keyword)

def handler404(request, exception=None):
    return render(request, '404.html', status=404)

def handler500(request):
    return render(request, '500.html', status=500)

def login_view(request):
    if request.user.is_authenticated:
        if not hasattr(request.user, 'dealer_profile'):
            return redirect('admin:index' if request.user.is_staff else 'home')
        return redirect('dealer_dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user:
            dealer_profile = getattr(user, 'dealer_profile', None)
            if dealer_profile is None:
                messages.error(request, 'Only dealer accounts can use this login page.')
                return redirect('login')
            if dealer_profile and dealer_profile.is_suspended:
                messages.error(request, 'Your account has been suspended.')
                return redirect('login')
            
            login(request, user)
            if dealer_profile and dealer_profile.must_change_password:
                return redirect('password_change')
            return redirect('dealer_dashboard')
        else:
            messages.error(request, 'Invalid credentials.')
    
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('home')

@login_required
def password_change_view(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.POST)
        if form.is_valid():
            old_password = form.cleaned_data.get('old_password')
            new_password = form.cleaned_data.get('new_password1')
            
            if request.user.check_password(old_password):
                request.user.set_password(new_password)
                request.user.save()
                if hasattr(request.user, 'dealer_profile'):
                    request.user.dealer_profile.must_change_password = False
                    request.user.dealer_profile.save()
                login(request, request.user)
                messages.success(request, 'Password changed successfully!')
                return redirect('dealer_dashboard')
            else:
                messages.error(request, 'Old password is incorrect.')
    else:
        form = PasswordChangeForm()
    
    return render(request, 'password_change.html', {'form': form})

def robots_txt(request):
    from django.http import HttpResponse
    return HttpResponse("User-agent: *\nAllow: /", content_type="text/plain")

def home(request):
    public_cars = Car.objects.visible_to_public().select_related('dealer', 'city').prefetch_related('images')
    featured_cars = public_cars.filter(is_featured=True)[:6]
    latest_cars = public_cars[:8]
    top_dealers = DealerProfile.objects.none()
    if not hasattr(request.user, 'dealer_profile'):
        top_dealers = DealerProfile.objects.filter(is_suspended=False)[:6]
    cities = City.objects.all()[:10]
    
    total_cars = Car.objects.available().count()
    total_dealers = DealerProfile.objects.filter(is_suspended=False).count()
    total_cities = City.objects.count()
    
    search_form = SearchForm()
    
    context = {
        'featured_cars': featured_cars,
        'latest_cars': latest_cars,
        'top_dealers': top_dealers,
        'cities': cities,
        'total_cars': total_cars,
        'total_dealers': total_dealers,
        'total_cities': total_cities,
        'search_form': search_form,
    }
    return render(request, 'home.html', context)

def car_list(request):
    cars = Car.objects.visible_to_public().select_related('dealer', 'city').prefetch_related('images')
    search_form = SearchForm(request.GET or None)
    
    # Handle hero search query
    q = request.GET.get('q', '')
    if q:
        cars = cars.filter(
            Q(brand__icontains=q) | 
            Q(model__icontains=q) | 
            Q(description__icontains=q) |
            Q(color__icontains=q)
        )
    
    if search_form.is_valid():
        brand = search_form.cleaned_data.get('brand')
        model = search_form.cleaned_data.get('model')
        year = search_form.cleaned_data.get('year')
        color = search_form.cleaned_data.get('color')
        city = search_form.cleaned_data.get('city')
        min_price = search_form.cleaned_data.get('min_price')
        max_price = search_form.cleaned_data.get('max_price')
        fuel_type = search_form.cleaned_data.get('fuel_type')
        transmission = search_form.cleaned_data.get('transmission')
        
        if brand:
            cars = cars.filter(brand__icontains=brand)
        if model:
            cars = cars.filter(model__icontains=model)
        if year:
            cars = cars.filter(year=year)
        if color:
            cars = cars.filter(color__icontains=color)
        if city:
            cars = cars.filter(city=city)
        if min_price:
            cars = cars.filter(price__gte=min_price)
        if max_price:
            cars = cars.filter(price__lte=max_price)
        if fuel_type:
            cars = cars.filter(fuel_type=fuel_type)
        if transmission:
            cars = cars.filter(transmission=transmission)

    search_keyword = get_search_keyword(request, search_form)
    record_car_search(search_keyword, cars.filter(is_sold=False))
    
    context = {
        'cars': cars,
        'search_form': search_form,
    }
    return render(request, 'car_list.html', context)

def car_detail(request, pk):
    car = get_object_or_404(
        Car.objects.select_related('dealer', 'dealer__city', 'city').prefetch_related('images'),
        pk=pk,
    )
    dealer_profile = getattr(request.user, 'dealer_profile', None)
    can_manage_car = dealer_profile and car.dealer_id == dealer_profile.id
    if not can_manage_car and not car.is_publicly_visible():
        raise Http404("Car not found")

    inquiry_form = InquiryForm()

    if request.method == 'GET':
        CarView.objects.create(car=car, visitor_ip=get_visitor_ip(request))
    
    if request.method == 'POST':
        if car.is_sold:
            messages.error(request, 'This car has already been sold.')
            return redirect('car_detail', pk=pk)
        inquiry_form = InquiryForm(request.POST)
        if inquiry_form.is_valid():
            inquiry = inquiry_form.save(commit=False)
            inquiry.car = car
            inquiry.save()
            messages.success(request, 'Your inquiry has been sent to the dealer!')
            return redirect('car_detail', pk=pk)
    
    context = {
        'car': car,
        'inquiry_form': inquiry_form,
    }
    return render(request, 'car_detail.html', context)


@require_POST
def car_click_analytics(request, pk):
    car = get_object_or_404(Car, pk=pk)
    dealer_profile = getattr(request.user, 'dealer_profile', None)
    can_manage_car = dealer_profile and car.dealer_id == dealer_profile.id
    if not can_manage_car and not car.is_publicly_visible():
        raise Http404("Car not found")

    click_type = request.POST.get('click_type')
    valid_click_types = {
        choice[0] for choice in CarClickAnalytics.CLICK_TYPE_CHOICES
    }
    if click_type not in valid_click_types:
        return JsonResponse({'error': 'Invalid click type.'}, status=400)

    CarClickAnalytics.objects.create(car=car, click_type=click_type)
    return JsonResponse({'ok': True})

def dealer_list(request):
    # Logged-in dealers should only see their own dealer profile.
    if hasattr(request.user, 'dealer_profile'):
        return redirect('dealer_detail', pk=request.user.dealer_profile.pk)
    
    dealers = DealerProfile.objects.filter(is_suspended=False)
    cities = City.objects.all()
    
    context = {
        'dealers': dealers,
        'cities': cities,
    }
    return render(request, 'dealer_list.html', context)

def dealer_detail(request, pk):
    dealer = get_object_or_404(DealerProfile, pk=pk)
    
    # Redirect logged-in dealers to their own profile when viewing others.
    can_manage_profile = False
    if request.user.is_authenticated:
        try:
            user_dealer = request.user.dealer_profile
            can_manage_profile = user_dealer.id == dealer.id
            if not can_manage_profile:
                return redirect('dealer_detail', pk=user_dealer.pk)
        except (DealerProfile.DoesNotExist, AttributeError):
            pass
    
    cars = dealer.cars.all() if can_manage_profile else dealer.cars.visible_to_public()
    
    context = {
        'dealer': dealer,
        'cars': cars,
        'can_manage_profile': can_manage_profile,
    }
    return render(request, 'dealer_detail.html', context)

def contact(request):
    from cars.forms import ContactForm
    form = ContactForm()
    
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            messages.success(request, 'Your message has been sent!')
            return redirect('contact')
    
    context = {'form': form}
    return render(request, 'contact.html', context)

@login_required
def dealer_dashboard(request):
    if not hasattr(request.user, 'dealer_profile'):
        messages.error(request, 'Only dealers can access this page.')
        return redirect('home')
    
    dealer = request.user.dealer_profile
    cars = dealer.cars.all()
    inquiries = Inquiry.objects.filter(car__dealer=dealer)
    today = timezone.now()
    recent_start = today - timedelta(days=7)
    previous_start = today - timedelta(days=14)

    analytics_cars = cars.select_related('city').annotate(
        total_views=Count('views', distinct=True),
        unique_visitors=Count(
            'views__visitor_ip',
            filter=Q(views__visitor_ip__isnull=False),
            distinct=True,
        ),
        total_searches=Count('searches', distinct=True),
        recent_searches=Count(
            'searches',
            filter=Q(searches__searched_at__gte=recent_start),
            distinct=True,
        ),
        previous_searches=Count(
            'searches',
            filter=Q(
                searches__searched_at__gte=previous_start,
                searches__searched_at__lt=recent_start,
            ),
            distinct=True,
        ),
        detail_clicks=Count(
            'clicks',
            filter=Q(clicks__click_type=CarClickAnalytics.VIEW_DETAILS),
            distinct=True,
        ),
        whatsapp_clicks=Count(
            'clicks',
            filter=Q(clicks__click_type=CarClickAnalytics.WHATSAPP),
            distinct=True,
        ),
        call_clicks=Count(
            'clicks',
            filter=Q(clicks__click_type=CarClickAnalytics.CALL),
            distinct=True,
        ),
        last_viewed_date=Max('views__viewed_at'),
        last_search_date=Max('searches__searched_at'),
    )
    car_performance = list(
        analytics_cars.order_by('-total_views', '-detail_clicks', '-whatsapp_clicks', 'brand', 'model')
    )
    most_searched_cars = list(
        analytics_cars.filter(total_searches__gt=0).order_by('-total_searches', '-last_search_date')[:5]
    )
    top_viewed_cars = list(
        analytics_cars.filter(total_views__gt=0).order_by('-total_views', '-last_viewed_date')[:5]
    )
    top_whatsapp_cars = list(
        analytics_cars.filter(whatsapp_clicks__gt=0).order_by('-whatsapp_clicks', 'brand', 'model')[:5]
    )

    most_viewed_car = top_viewed_cars[0] if top_viewed_cars else None
    most_searched_car = most_searched_cars[0] if most_searched_cars else None

    chart_cars = car_performance[:8]
    search_chart_cars = most_searched_cars[:5]
    
    context = {
        'dealer': dealer,
        'cars': cars,
        'inquiries': inquiries,
        'car_performance': car_performance,
        'most_searched_cars': most_searched_cars,
        'top_viewed_cars': top_viewed_cars,
        'top_whatsapp_cars': top_whatsapp_cars,
        'high_demand_search_threshold': HIGH_DEMAND_SEARCH_THRESHOLD,
        'dashboard_stats': {
            'total_cars': cars.count(),
            'available_cars': cars.filter(is_sold=False).count(),
            'sold_cars': cars.filter(is_sold=True).count(),
            'total_car_views': CarView.objects.filter(car__dealer=dealer).count(),
            'total_car_searches': CarSearch.objects.filter(matched_car__dealer=dealer).count(),
            'most_viewed_car': most_viewed_car,
            'most_searched_car': most_searched_car,
        },
        'search_chart_labels': [get_car_name(car) for car in search_chart_cars],
        'search_chart_counts': [car.total_searches for car in search_chart_cars],
        'performance_chart_labels': [get_car_name(car) for car in chart_cars],
        'performance_view_counts': [car.total_views for car in chart_cars],
        'performance_whatsapp_counts': [car.whatsapp_clicks for car in chart_cars],
        'performance_call_counts': [car.call_clicks for car in chart_cars],
    }
    return render(request, 'dealer_dashboard.html', context)

@login_required
def car_create(request):
    if not hasattr(request.user, 'dealer_profile'):
        messages.error(request, 'Only dealers can add cars.')
        return redirect('home')
    
    dealer = request.user.dealer_profile
    if request.method == 'POST':
        car_form = CarForm(request.POST)
        
        if car_form.is_valid():
            car = car_form.save(commit=False)
            car.dealer = dealer
            car.save()
            
            images = request.FILES.getlist('image')
            for i, image in enumerate(images):
                CarImage.objects.create(car=car, image=image, is_primary=(i == 0))
            
            messages.success(request, 'Car listing added successfully!')
            return redirect('dealer_dashboard')
    else:
        car_form = CarForm()
    
    context = {
        'car_form': car_form,
    }
    return render(request, 'car_form.html', context)

@login_required
def car_edit(request, pk):
    if not hasattr(request.user, 'dealer_profile'):
        messages.error(request, 'Only dealers can edit cars.')
        return redirect('home')
    
    car = get_object_or_404(Car, pk=pk, dealer=request.user.dealer_profile)
    
    if request.method == 'POST':
        car_form = CarForm(request.POST, instance=car)
        
        if car_form.is_valid():
            car = car_form.save()

            delete_image_ids = request.POST.getlist('delete_images')
            if delete_image_ids:
                car.images.filter(id__in=delete_image_ids).delete()

            images = request.FILES.getlist('image')
            needs_primary = not car.images.filter(is_primary=True).exists()
            for i, image in enumerate(images):
                CarImage.objects.create(
                    car=car,
                    image=image,
                    is_primary=(needs_primary and i == 0),
                )

            if not car.images.filter(is_primary=True).exists() and car.images.exists():
                primary_image = car.images.first()
                primary_image.is_primary = True
                primary_image.save(update_fields=['is_primary'])

            messages.success(request, 'Car listing updated successfully!')
            return redirect('dealer_dashboard')
    else:
        car_form = CarForm(instance=car)
    
    context = {
        'car_form': car_form,
        'car': car,
    }
    return render(request, 'car_form.html', context)

@login_required
def car_delete(request, pk):
    if not hasattr(request.user, 'dealer_profile'):
        messages.error(request, 'Only dealers can delete cars.')
        return redirect('home')
    
    car = get_object_or_404(Car, pk=pk, dealer=request.user.dealer_profile)
    
    if request.method == 'POST':
        car.delete()
        messages.success(request, 'Car listing deleted successfully!')
        return redirect('dealer_dashboard')
    
    context = {'car': car}
    return render(request, 'car_confirm_delete.html', context)

@login_required
@require_POST
def car_mark_sold(request, pk):
    if not hasattr(request.user, 'dealer_profile'):
        messages.error(request, 'Only dealers can update car status.')
        return redirect('home')
    
    car = get_object_or_404(Car, pk=pk, dealer=request.user.dealer_profile)
    car.mark_sold()
    messages.success(request, f'{car} marked as sold!')
    return redirect('dealer_dashboard')

@login_required
@require_POST
def car_mark_available(request, pk):
    if not hasattr(request.user, 'dealer_profile'):
        messages.error(request, 'Only dealers can update car status.')
        return redirect('home')
    
    car = get_object_or_404(Car, pk=pk, dealer=request.user.dealer_profile)
    car.mark_available()
    messages.success(request, f'{car} marked as available!')
    return redirect('dealer_dashboard')

@login_required
def dealer_profile_view(request):
    if not hasattr(request.user, 'dealer_profile'):
        messages.error(request, 'Only dealers can access this page.')
        return redirect('home')
    
    dealer = request.user.dealer_profile
    
    if request.method == 'POST':
        from cars.forms import DealerProfileForm
        form = DealerProfileForm(request.POST, request.FILES, instance=dealer)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('dealer_profile')
    else:
        from cars.forms import DealerProfileForm
        form = DealerProfileForm(instance=dealer)
    
    context = {'form': form}
    return render(request, 'dealer_profile_edit.html', context)
