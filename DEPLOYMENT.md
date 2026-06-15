# Khpal Buner - Deployment Guide

## Prerequisites
- Python 3.10+
- PostgreSQL (or SQLite for development)
- pip

## Installation

1. Clone the repository
```bash
git clone <repository-url>
cd khpalbuner
```

2. Create virtual environment
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
.\venv\Scripts\activate  # Windows
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Environment setup
Create `.env` file (for production):
```
SECRET_KEY=your-secret-key-here
DEBUG=False
DATABASE_URL=postgresql://user:password@localhost/khpalbuner
```

5. Run migrations
```bash
python manage.py migrate
```

6. Create superuser
```bash
python manage.py createsuperuser
```

7. Run development server
```bash
python manage.py runserver
```

## Production Deployment (Linux/Apache)

1. Install dependencies
```bash
sudo apt install python3-pip python3-venv postgresql postgresql-contrib
```

2. Collect static files
```bash
python manage.py collectstatic
```

3. Configure Apache with mod_wsgi
```apache
<VirtualHost *:80>
    ServerName yourdomain.com
    DocumentRoot /path/to/khpalbuner
    
    WSGIDaemonProcess khpalbuner python-path=/path/to/khpalbuner python-home=/path/to/khpalbuner/venv
    WSGIProcessGroup khpalbuner
    WSGIScriptAlias / /path/to/khpalbuner/khpalbuner/wsgi.py
    
    Alias /static /path/to/khpalbuner/staticfiles
    <Directory /path/to/khpalbuner/staticfiles>
        Require all granted
    </Directory>
    
    <Directory /path/to/khpalbuner/khpalbuner>
        <Files wsgi.py>
            Require all granted
        </Files>
    </Directory>
</VirtualHost>
```

4. Set permissions
```bash
sudo chown -R www-data:www-data /path/to/khpalbuner
sudo chmod -R 755 /path/to/khpalbuner
```

## Creating Dealer Accounts (Admin)

1. Go to Admin Panel: `/admin/`
2. Click "Add" next to Users
3. Fill user details (username, password)
4. Add DealerProfile information (shop name, phone, address, etc.)
5. The dealer can log in and manage their cars

## Website Structure

- `/` - Home page
- `/cars/` - Car listings
- `/cars/<id>/` - Car detail page
- `/dealers/` - Dealer list
- `/dealer/<id>/` - Dealer profile
- `/contact/` - Contact form
- `/dashboard/` - Dealer dashboard (login required)
- `/login/` - Dealer login
- `/logout/` - Logout

## Features

- **Search**: Search by brand, model, year, color, city, price range, fuel type, transmission
- **Favorites**: Saved in browser localStorage
- **Compare**: Compare cars side-by-side (localStorage)
- **Inquiries**: Store customer inquiries in database
- **Featured Cars**: Admin can mark cars as featured
- **SEO**: Sitemap, robots.txt, meta tags included