# Khpal Buner - Quick Start Guide

## What is Khpal Buner?

Khpal Buner is a car marketplace platform that connects local car dealers with customers. It allows:
- Dealers to list their cars with images and details
- Customers to search and view cars from multiple dealers
- Users to contact dealers directly through inquiries

## Quick Start (5 minutes)

### 1. Start the Server
```bash
python manage.py runserver
```

Visit: http://localhost:8000

### 2. Create Admin Account
```bash
python manage.py createsuperuser
```

Visit: http://localhost:8000/admin

### 3. Create Cities (Optional - Already Pre-loaded)
```bash
python manage.py setup_initial_data
```

### 4. Create Dealer Account (in Admin)
- Go to Admin > Users > Add User
- Set username and password
- Save
- Go to Dealer Profiles > Add Dealer Profile
- Link user to dealer profile
- Add shop details

### 5. Dealer Features
After login (http://localhost:8000/login):
- **Dashboard**: View all your cars and inquiries
- **Add Car**: Upload new listings with images
- **Edit/Delete**: Manage existing listings
- **Mark Sold/Available**: Update car status
- **Profile**: Edit dealer information

## Project Features

### For Customers
✓ Search cars by brand, model, year, color, city, price, fuel type, transmission
✓ View detailed car information with image gallery
✓ See dealer information and location
✓ Contact dealers via WhatsApp or phone
✓ Send inquiries to dealers
✓ View featured and latest cars
✓ Browse dealers by city
✓ Responsive mobile design

### For Dealers
✓ Login with credentials
✓ Manage car listings
✓ Upload multiple images per car
✓ Track customer inquiries
✓ Mark cars as sold/available
✓ Update profile information
✓ Manage shop details and location

### For Admin
✓ Manage all users and dealers
✓ Suspend dealer accounts
✓ Manage car listings
✓ View all inquiries
✓ Manage cities
✓ View system statistics

## File Structure

```
bargin/
├── manage.py                 # Django management
├── db.sqlite3               # Database
├── requirements.txt         # Python dependencies
├── README.md               # Main documentation
├── INSTALLATION.md         # Installation guide
├── DEPLOYMENT.md           # Deployment guide
├── QUICKSTART.md           # This file
│
├── cars/                   # Main Django app
│   ├── models.py          # Database models
│   ├── views.py           # View logic
│   ├── forms.py           # Django forms
│   ├── admin.py           # Admin configuration
│   ├── utils.py           # Helper functions
│   ├── sitemaps.py        # SEO sitemaps
│   └── management/commands/
│       └── setup_initial_data.py
│
├── khpalbuner/             # Project settings
│   ├── settings.py        # Configuration
│   ├── urls.py            # URL routing
│   ├── context_processors.py
│   └── templates/         # HTML templates
│       ├── base.html      # Base template
│       ├── home.html
│       ├── car_list.html
│       ├── car_detail.html
│       ├── dealer_list.html
│       ├── dealer_detail.html
│       ├── login.html
│       ├── dealer_dashboard.html
│       ├── car_form.html
│       ├── dealer_profile_edit.html
│       ├── password_change.html
│       ├── contact.html
│       ├── 404.html
│       └── 500.html
│
└── khpalbuner/static/
    ├── css/
    │   └── style.css      # Main styles
    ├── js/
    │   └── main.js        # JavaScript
    └── img/
        ├── no-image.jpg   # Placeholder image
        └── og-image.jpg   # Social sharing image
```

## Common Tasks

### Add a New City
```bash
python manage.py shell
>>> from cars.models import City
>>> City.objects.create(name='Your City')
>>> exit()
```

### Create Test Dealer
```bash
python manage.py shell
>>> from django.contrib.auth.models import User
>>> from cars.models import DealerProfile, City
>>> user = User.objects.create_user('testdealer', 'test@test.com', 'password123')
>>> city = City.objects.get(name='Karachi')
>>> dealer = DealerProfile.objects.create(
...     user=user,
...     shop_name='Test Motors',
...     owner_name='John Doe',
...     phone='03001234567',
...     address='123 Street',
...     city=city
... )
>>> exit()
```

### Delete All Test Data
```bash
python manage.py shell
>>> from cars.models import Car
>>> Car.objects.all().delete()
>>> exit()
```

## Troubleshooting

### Port Already in Use
```bash
python manage.py runserver 8001  # Use different port
```

### Database Issues
```bash
python manage.py migrate --run-syncdb
python manage.py migrate
```

### Collect Static Files
```bash
python manage.py collectstatic --noinput
```

## Environment Variables

Create a `.env` file with:
```
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

## Important URLs

- Home: http://localhost:8000/
- Cars: http://localhost:8000/cars/
- Dealers: http://localhost:8000/dealers/
- Contact: http://localhost:8000/contact/
- Admin: http://localhost:8000/admin/
- Dealer Login: http://localhost:8000/login/
- Sitemap: http://localhost:8000/sitemap.xml
- Robots: http://localhost:8000/robots.txt

## Need Help?

1. Check README.md for detailed information
2. Check DEPLOYMENT.md for production setup
3. Check INSTALLATION.md for setup instructions
4. Review Django documentation: https://docs.djangoproject.com/

## Next Steps

1. Customize the styling in `static/css/style.css`
2. Add more features as needed
3. Deploy to production using DEPLOYMENT.md
4. Set up proper email configuration
5. Configure security settings for production
