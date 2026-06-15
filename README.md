# Khpal Buner - Car Marketplace

A fully functional car marketplace website where verified local car dealers can upload their car listings, and customers can search and view cars from multiple dealers in one place.

## Project Structure

```
khpalbuner/
├── manage.py
├── requirements.txt
├── khpalbuner/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   ├── asgi.py
│   ├── templates/
│   │   ├── base.html
│   │   ├── home.html
│   │   ├── car_list.html
│   │   ├── car_detail.html
│   │   ├── dealer_list.html
│   │   ├── dealer_detail.html
│   │   ├── contact.html
│   │   ├── login.html
│   │   ├── password_change.html
│   │   ├── dealer_dashboard.html
│   │   ├── car_form.html
│   │   ├── car_confirm_delete.html
│   │   ├── dealer_profile_edit.html
│   │   ├── 404.html
│   │   └── 500.html
│   └── static/
│       ├── css/
│       │   └── style.css
│       ├── js/
│       │   └── main.js
│       └── img/
│           ├── no-image.jpg
│           └── og-image.jpg
└── cars/
    ├── __init__.py
    ├── admin.py
    ├── apps.py
    ├── forms.py
    ├── models.py
    ├── sitemaps.py
    ├── tests.py
    └── views.py
```

## Features

- **User Roles**: Admin, Dealer, Customer (no login required)
- **Search**: Brand, model, year, color, city, price, fuel type, transmission
- **Responsive Design**: Bootstrap 5
- **Image Gallery**: Car image sliders
- **Favorites**: Local storage based
- **Comparison**: Compare cars side-by-side
- **Inquiries**: Contact dealers via form
- **Google Maps**: Dealer location mapping
- **SEO**: Sitemap, robots.txt, meta tags

## Technology Stack

- Python (Django 5+)
- PostgreSQL/SQLite
- Bootstrap 5
- HTML5/CSS3
- Vanilla JavaScript

## Setup

1. `pip install -r requirements.txt`
2. `python manage.py migrate`
3. `python manage.py createsuperuser`
4. `python manage.py runserver`

## Admin Workflow

1. Admin creates dealer accounts manually via `/admin/`
2. Dealer logs in with provided credentials
3. Dealer must change password on first login
4. Dealer can add/edit/delete cars

See DEPLOYMENT.md for production deployment instructions.