from datetime import timedelta

from django.test import TestCase
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
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


class CityModelTest(TestCase):
    """Test City model"""
    
    def setUp(self):
        self.city = City.objects.create(name='Karachi')
    
    def test_city_creation(self):
        self.assertEqual(self.city.name, 'Karachi')
    
    def test_city_str(self):
        self.assertEqual(str(self.city), 'Karachi')


class DealerProfileModelTest(TestCase):
    """Test DealerProfile model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='dealer1',
            password='testpass123'
        )
        self.city = City.objects.create(name='Karachi')
        self.dealer = DealerProfile.objects.create(
            user=self.user,
            shop_name='Test Motors',
            owner_name='Ahmed Khan',
            phone='03001234567',
            address='123 Main St',
            city=self.city
        )
    
    def test_dealer_creation(self):
        self.assertEqual(self.dealer.shop_name, 'Test Motors')
        self.assertEqual(self.dealer.owner_name, 'Ahmed Khan')
    
    def test_dealer_str(self):
        self.assertEqual(str(self.dealer), 'Test Motors')

    def test_google_maps_embed_url_uses_coordinates_from_normal_maps_link(self):
        self.dealer.google_maps_link = 'https://www.google.com/maps/place/Test+Motors/@34.5032,72.4848,17z/'

        embed_url = self.dealer.get_google_maps_embed_url()

        self.assertEqual(embed_url, 'https://www.google.com/maps?q=34.5032%2C72.4848&output=embed')

    def test_google_maps_embed_url_keeps_existing_embed_link(self):
        self.dealer.google_maps_link = 'https://www.google.com/maps/embed?pb=test'

        embed_url = self.dealer.get_google_maps_embed_url()

        self.assertEqual(embed_url, self.dealer.google_maps_link)

    def test_google_maps_embed_url_falls_back_to_address_for_short_links(self):
        self.dealer.google_maps_link = 'https://maps.app.goo.gl/example'

        embed_url = self.dealer.get_google_maps_embed_url()

        self.assertEqual(embed_url, 'https://www.google.com/maps?q=123+Main+St+Karachi&output=embed')


class CarModelTest(TestCase):
    """Test Car model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='dealer1',
            password='testpass123'
        )
        self.city = City.objects.create(name='Karachi')
        self.dealer = DealerProfile.objects.create(
            user=self.user,
            shop_name='Test Motors',
            owner_name='Ahmed Khan',
            phone='03001234567',
            address='123 Main St',
            city=self.city
        )
        self.car = Car.objects.create(
            dealer=self.dealer,
            brand='Honda',
            model='Civic',
            year=2022,
            color='White',
            price=2500000,
            mileage=50000,
            fuel_type='petrol',
            transmission='automatic',
            description='Nice car',
            city=self.city
        )
    
    def test_car_creation(self):
        self.assertEqual(self.car.brand, 'Honda')
        self.assertEqual(self.car.model, 'Civic')
    
    def test_car_str(self):
        self.assertEqual(str(self.car), '2022 Honda Civic')

    def test_sold_car_sets_sold_at(self):
        self.car.mark_sold()
        self.car.refresh_from_db()

        self.assertTrue(self.car.is_sold)
        self.assertIsNotNone(self.car.sold_at)

    def test_available_car_clears_sold_at(self):
        self.car.mark_sold()
        self.car.mark_available()
        self.car.refresh_from_db()

        self.assertFalse(self.car.is_sold)
        self.assertIsNone(self.car.sold_at)

    def test_public_visibility_hides_sold_cars_after_24_hours(self):
        recent_sold = Car.objects.create(
            dealer=self.dealer,
            brand='Toyota',
            model='Yaris',
            year=2021,
            color='Silver',
            price=2000000,
            mileage=30000,
            fuel_type='petrol',
            transmission='automatic',
            description='Recently sold car',
            city=self.city,
            is_sold=True,
            sold_at=timezone.now() - timedelta(hours=23),
        )
        old_sold = Car.objects.create(
            dealer=self.dealer,
            brand='Suzuki',
            model='Mehran',
            year=2018,
            color='White',
            price=900000,
            mileage=80000,
            fuel_type='petrol',
            transmission='manual',
            description='Old sold car',
            city=self.city,
            is_sold=True,
            sold_at=timezone.now() - timedelta(hours=25),
        )

        visible_cars = Car.objects.visible_to_public()
        self.assertIn(self.car, visible_cars)
        self.assertIn(recent_sold, visible_cars)
        self.assertNotIn(old_sold, visible_cars)


class InquiryModelTest(TestCase):
    """Test Inquiry model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='dealer1',
            password='testpass123'
        )
        self.city = City.objects.create(name='Karachi')
        self.dealer = DealerProfile.objects.create(
            user=self.user,
            shop_name='Test Motors',
            owner_name='Ahmed Khan',
            phone='03001234567',
            address='123 Main St',
            city=self.city
        )
        self.car = Car.objects.create(
            dealer=self.dealer,
            brand='Honda',
            model='Civic',
            year=2022,
            color='White',
            price=2500000,
            mileage=50000,
            fuel_type='petrol',
            transmission='automatic',
            description='Nice car',
            city=self.city
        )
        self.inquiry = Inquiry.objects.create(
            car=self.car,
            name='John Doe',
            phone='03001234567',
            message='Is this car available?'
        )
    
    def test_inquiry_creation(self):
        self.assertEqual(self.inquiry.name, 'John Doe')
        self.assertEqual(self.inquiry.is_read, False)


class ViewsTest(TestCase):
    """Test views"""
    
    def setUp(self):
        self.city = City.objects.create(name='Karachi')
        self.user = User.objects.create_user(
            username='dealer1',
            password='testpass123'
        )
        self.dealer = DealerProfile.objects.create(
            user=self.user,
            shop_name='Test Motors',
            owner_name='Ahmed Khan',
            phone='03001234567',
            address='123 Main St',
            city=self.city,
            must_change_password=False
        )
    
    def test_home_view(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
    
    def test_car_list_view(self):
        response = self.client.get('/cars/')
        self.assertEqual(response.status_code, 200)
    
    def test_dealer_list_view(self):
        response = self.client.get('/dealers/')
        self.assertEqual(response.status_code, 200)
    
    def test_dealer_list_redirects_logged_in_dealer(self):
        self.client.login(username='dealer1', password='testpass123')
        response = self.client.get('/dealers/', follow=False)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, f'/dealer/{self.dealer.pk}/')
    
    def test_dealer_detail_redirects_logged_in_dealer_to_own_profile(self):
        self.client.login(username='dealer1', password='testpass123')
        other_city = City.objects.create(name='Lahore')
        other_user = User.objects.create_user(username='dealer2', password='testpass123')
        other_dealer = DealerProfile.objects.create(
            user=other_user,
            shop_name='Other Motors',
            owner_name='Other Owner',
            phone='03001234567',
            address='456 Other St',
            city=other_city,
            must_change_password=False
        )
        response = self.client.get(f'/dealer/{other_dealer.pk}/', follow=False)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, f'/dealer/{self.dealer.pk}/')

    def test_logged_in_dealer_can_view_only_own_profile(self):
        self.client.login(username='dealer1', password='testpass123')

        response = self.client.get(f'/dealer/{self.dealer.pk}/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Motors')
        self.assertContains(response, 'Edit Profile')
    
    def test_contact_view(self):
        response = self.client.get('/contact/')
        self.assertEqual(response.status_code, 200)

    def test_dealer_can_create_car_with_image(self):
        self.client.login(username='dealer1', password='testpass123')
        image = SimpleUploadedFile(
            'car.gif',
            b'GIF87a\x01\x00\x01\x00\x80\x01\x00\x00\x00\x00\xff\xff\xff,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;',
            content_type='image/gif'
        )

        response = self.client.post('/car/add/', {
            'brand': 'Toyota',
            'model': 'Corolla',
            'year': 2023,
            'color': 'White',
            'price': 3500000,
            'mileage': 12000,
            'fuel_type': 'petrol',
            'transmission': 'automatic',
            'description': 'Clean family car',
            'city': self.city.pk,
            'image': image,
        })

        self.assertEqual(response.status_code, 302)
        car = Car.objects.get(brand='Toyota', model='Corolla')
        self.assertEqual(car.images.count(), 1)
        self.assertTrue(car.images.first().is_primary)

    def test_dealer_can_upload_profile_picture(self):
        self.client.login(username='dealer1', password='testpass123')
        image = SimpleUploadedFile(
            'dealer.gif',
            b'GIF87a\x01\x00\x01\x00\x80\x01\x00\x00\x00\x00\xff\xff\xff,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;',
            content_type='image/gif'
        )

        response = self.client.post('/profile/', {
            'shop_name': 'Updated Motors',
            'owner_name': 'Ahmed Khan',
            'profile_picture': image,
            'phone': '03001234567',
            'whatsapp': '',
            'address': '123 Main St',
            'city': self.city.pk,
            'google_maps_link': '',
        })

        self.dealer.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.dealer.shop_name, 'Updated Motors')
        self.assertTrue(self.dealer.profile_picture.name.startswith('dealers/'))

    def test_dealer_can_mark_own_car_sold(self):
        car = Car.objects.create(
            dealer=self.dealer,
            brand='Honda',
            model='City',
            year=2022,
            color='Black',
            price=2800000,
            mileage=18000,
            fuel_type='petrol',
            transmission='automatic',
            description='Dealer car',
            city=self.city,
        )
        self.client.login(username='dealer1', password='testpass123')

        response = self.client.post(f'/car/{car.pk}/sold/')
        car.refresh_from_db()

        self.assertEqual(response.status_code, 302)
        self.assertTrue(car.is_sold)
        self.assertIsNotNone(car.sold_at)

    def test_old_sold_car_is_hidden_from_public_list_and_detail(self):
        old_sold = Car.objects.create(
            dealer=self.dealer,
            brand='Hidden',
            model='Sold',
            year=2020,
            color='Gray',
            price=1500000,
            mileage=45000,
            fuel_type='petrol',
            transmission='manual',
            description='Expired sold listing',
            city=self.city,
            is_sold=True,
            sold_at=timezone.now() - timedelta(hours=25),
        )

        list_response = self.client.get('/cars/')
        detail_response = self.client.get(f'/cars/{old_sold.pk}/')

        self.assertEqual(list_response.status_code, 200)
        self.assertNotContains(list_response, 'Hidden')
        self.assertEqual(detail_response.status_code, 404)

    def test_recent_sold_car_stays_visible_for_24_hours(self):
        recent_sold = Car.objects.create(
            dealer=self.dealer,
            brand='Recent',
            model='Sold',
            year=2020,
            color='Blue',
            price=1600000,
            mileage=42000,
            fuel_type='petrol',
            transmission='manual',
            description='Recent sold listing',
            city=self.city,
            is_sold=True,
            sold_at=timezone.now() - timedelta(hours=23),
        )

        list_response = self.client.get('/cars/')
        detail_response = self.client.get(f'/cars/{recent_sold.pk}/')

        self.assertEqual(list_response.status_code, 200)
        self.assertContains(list_response, 'Recent')
        self.assertEqual(detail_response.status_code, 200)

    def test_car_search_records_matched_cars(self):
        matching_car = Car.objects.create(
            dealer=self.dealer,
            brand='Toyota',
            model='Vitz',
            year=2020,
            color='White',
            price=2200000,
            mileage=30000,
            fuel_type='petrol',
            transmission='automatic',
            description='Compact city car',
            city=self.city,
        )
        Car.objects.create(
            dealer=self.dealer,
            brand='Honda',
            model='Civic',
            year=2022,
            color='Black',
            price=4200000,
            mileage=18000,
            fuel_type='petrol',
            transmission='automatic',
            description='Sedan',
            city=self.city,
        )

        response = self.client.get('/cars/', {'brand': 'Toyota'})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(CarSearch.objects.count(), 1)
        search = CarSearch.objects.get()
        self.assertEqual(search.matched_car, matching_car)
        self.assertIn('Brand: Toyota', search.search_keyword)

    def test_car_detail_records_view_with_visitor_ip(self):
        car = Car.objects.create(
            dealer=self.dealer,
            brand='Honda',
            model='City',
            year=2022,
            color='Black',
            price=2800000,
            mileage=18000,
            fuel_type='petrol',
            transmission='automatic',
            description='Dealer car',
            city=self.city,
        )

        response = self.client.get(f'/cars/{car.pk}/', REMOTE_ADDR='10.0.0.5')

        self.assertEqual(response.status_code, 200)
        view = CarView.objects.get(car=car)
        self.assertEqual(view.visitor_ip, '10.0.0.5')

    def test_car_click_analytics_records_valid_click(self):
        car = Car.objects.create(
            dealer=self.dealer,
            brand='Suzuki',
            model='Alto',
            year=2021,
            color='Silver',
            price=2100000,
            mileage=12000,
            fuel_type='petrol',
            transmission='automatic',
            description='Small car',
            city=self.city,
        )

        response = self.client.post(
            f'/cars/{car.pk}/track-click/',
            {'click_type': CarClickAnalytics.WHATSAPP},
        )

        self.assertEqual(response.status_code, 200)
        click = CarClickAnalytics.objects.get(car=car)
        self.assertEqual(click.click_type, CarClickAnalytics.WHATSAPP)

    def test_dealer_dashboard_includes_analytics_summary(self):
        car = Car.objects.create(
            dealer=self.dealer,
            brand='Toyota',
            model='Corolla',
            year=2023,
            color='White',
            price=3500000,
            mileage=12000,
            fuel_type='petrol',
            transmission='automatic',
            description='Clean family car',
            city=self.city,
        )
        CarView.objects.create(car=car, visitor_ip='10.0.0.5')
        CarSearch.objects.create(search_keyword='Toyota', matched_car=car)
        CarClickAnalytics.objects.create(car=car, click_type=CarClickAnalytics.CALL)
        self.client.login(username='dealer1', password='testpass123')

        response = self.client.get('/dashboard/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Most Searched Cars')
        self.assertEqual(response.context['dashboard_stats']['total_car_views'], 1)
        self.assertEqual(response.context['dashboard_stats']['total_car_searches'], 1)
        self.assertEqual(response.context['car_performance'][0].call_clicks, 1)

