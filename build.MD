"Act as a Principal Django Architect and E-Commerce Lead. I am building the MVP for Warm Hook Hugs, a premium handcrafted crochet and knitwear brand based in Pakistan. We are building a high-performance, maintainable Django web application aimed at a premium market.

Please provide the complete project architecture, folder structure, and the exact Python code for the core apps (models.py, views.py, urls.py). The MVP scope is strictly locked to the following requirements:

1. Tech Stack:

Backend: Django 5.x, Python.

Database: SQLite for local dev, mapping to PostgreSQL for production.

Frontend: Django Templates using Tailwind CSS via CDN for rapid, premium, and responsive UI development.

Admin: We will use Django’s out-of-the-box Admin panel as our initial 'Management & Support' portal to manage inventory and orders. Do not build a custom dashboard.

2. Database Schema (models.py):

Category: Name, Slug. (Categories will include: The Hug Collection, Warmth & Wear, Home & Hearth).

Product: Title, Slug, Premium Description, Price (in PKR), Stock Quantity, High-res ImageField, and a Foreign Key to Category.

Order & OrderItem: Tracking customer details, shipping address, total bill, and Order Status (Pending, OTP Verified, Shipped, Delivered).

3. Payments & OTP Logic (Crucial for Pakistan):

The only payment method for Version 1.0 is Cash on Delivery (COD).

To prevent fake orders, we must have an OTP verification step.

Write the view logic that takes the user's phone number at checkout, generates a 6-digit random code, saves it temporarily (using Django sessions or caching), and simulates sending it via an SMS API (like MoceanAPI or Twilio). The order status should only change from 'Pending' to 'OTP Verified' once the user inputs the correct code.

4. Deliverables:
Please write the complete code for:

models.py (Products, Orders, Categories).

views.py (Specifically the Cart Checkout and OTP verification logic).

The optimal Django project structure.
Keep the code clean, modular, and extensively commented."


"Act as a Principal DevOps Engineer and Django Architect. I am building the production MVP for Warm Hook Hugs, a premium e-commerce brand. I need a fully containerized, production-ready Django deployment stack that I can deploy on a fresh Ubuntu server with a single bash script.

Do not explain basic Django concepts. Provide the exact files and code required for a highly secure, scalable architecture using Docker, Docker Compose, PostgreSQL, Gunicorn, Nginx, and Let's Encrypt (Certbot) for SSL.

Please generate the following deliverables:

1. Dockerfile (Production-Optimized):

Use a lightweight multi-stage build (e.g., python:3.12-slim).

Install libpq-dev and compile dependencies.

Set up a non-root user for security.

Use Gunicorn as the WSGI HTTP server binding to port 8000.

2. docker-compose.yml:

Define 4 services: web (Django + Gunicorn), db (PostgreSQL 15), nginx (Reverse Proxy), and certbot (for SSL generation/renewal).

Map necessary volumes for Postgres data, static files, media files (for product images), and Certbot challenges.

Pass environment variables securely via a .env.prod file.

3. nginx/default.conf:

Configure Nginx to listen on port 80 and redirect to 443 (HTTPS).

Proxy pass requests to the Gunicorn web container.

Serve /static/ and /media/ directories directly for maximum speed.

Include the configuration required for Certbot's ACME challenge.

4. settings.py (Production Snippet):

Write the production-specific settings for Django using dj-database-url for the database and python-decouple for reading environment variables (SECRET_KEY, DEBUG=False, ALLOWED_HOSTS, CSRF_TRUSTED_ORIGINS).

5. deploy.sh (The Magic Script):

Write an executable bash script that I can run on a fresh Ubuntu server.

The script must: update packages, install Docker and Docker Compose, copy a template .env file, run docker-compose up -d --build, execute Django migrations (docker-compose exec web python manage.py migrate), collect static files, and create a Django superuser.