# Installation Guide - Khpal Buner

## Prerequisites
- Python 3.10+
- pip (Python Package Manager)

## Installation Steps

### 1. Clone or Extract the Project
```bash
cd bargin
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
```bash
cp .env.example .env
# Edit .env file with your settings
```

### 5. Apply Migrations
```bash
python manage.py migrate
```

### 6. Create Superuser
```bash
python manage.py createsuperuser
```

### 7. Collect Static Files
```bash
python manage.py collectstatic --noinput
```

### 8. Create Sample Cities
```bash
python manage.py shell
>>> from cars.models import City
>>> City.objects.create(name='Karachi')
>>> City.objects.create(name='Lahore')
>>> City.objects.create(name='Islamabad')
>>> exit()
```

### 9. Run Development Server
```bash
python manage.py runserver
```

Visit http://localhost:8000 in your browser.

## Access Admin Panel
- URL: http://localhost:8000/admin
- Username/Password: Use the superuser credentials you created

## Project Structure
- `cars/` - Main app containing models, views, and forms
- `khpalbuner/` - Project configuration and templates
- `static/` - CSS, JavaScript, and Images
- `templates/` - HTML templates
- `db.sqlite3` - Development database

## Creating Admin User for Dealer Account
1. Go to admin panel
2. Create a new user under "Users"
3. Create a dealer profile linked to that user
4. Set `must_change_password` to True if you want them to change password on first login

## Features
- Car listing management
- Dealer profiles and authentication
- Advanced search with filters
- City-based categorization
- Image gallery for cars
- Inquiry management
- Responsive design
- SEO optimization with sitemaps

## Support
For issues or questions, please refer to README.md or DEPLOYMENT.md
