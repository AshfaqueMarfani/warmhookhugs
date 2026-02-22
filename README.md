<p align="center">
  <img src="static/images/favicon.svg" width="80" alt="Warm Hook Hugs Logo">
</p>

<h1 align="center">Warm Hook Hugs</h1>

<p align="center">
  <strong>Premium Handcrafted Crochet & Knitwear — E-Commerce Platform</strong><br>
  A full-stack Django application built from scratch for a real artisan brand in Pakistan.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Django-5.2-092E20?style=for-the-badge&logo=django&logoColor=white" alt="Django 5.2">
  <img src="https://img.shields.io/badge/Python-3.13-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.13">
  <img src="https://img.shields.io/badge/Tailwind_CSS-3.x-06B6D4?style=for-the-badge&logo=tailwindcss&logoColor=white" alt="Tailwind CSS">
  <img src="https://img.shields.io/badge/PostgreSQL-15-336791?style=for-the-badge&logo=postgresql&logoColor=white" alt="PostgreSQL">
  <img src="https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker&logoColor=white" alt="Docker">
</p>

---

## Overview

**Warm Hook Hugs** is a production-grade e-commerce platform designed for a premium handcrafted crochet brand based in Pakistan. The project demonstrates end-to-end Django development — from database architecture and business logic to responsive UI, payment integration, and deployment infrastructure.

This is **not a tutorial project**. It's a complete, deployable storefront with real-world features like OTP-verified checkout, multiple Pakistani payment gateways, shipping rate calculation, coupon management, and a full admin dashboard.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Django 5.2, Python 3.13 |
| **Frontend** | Django Templates, Tailwind CSS (CDN), Vanilla JS |
| **Database** | SQLite (dev) / PostgreSQL 15 (prod) |
| **Payments** | Stripe, EasyPaisa, JazzCash, Cash on Delivery |
| **OTP Verification** | WhatsApp Business API (console fallback for dev) |
| **Deployment** | Docker, Gunicorn, Nginx, docker-compose |
| **Fonts** | Playfair Display, DM Sans (Google Fonts) |
| **Config** | python-decouple (`.env` based settings) |

---

## Architecture at a Glance

```
10 models · 46 views · 41 URL routes · 30 templates · 4 service modules
```

```
warmhookhugs/
├── config/                  # Django project settings, ASGI/WSGI
│   ├── settings.py          # Environment-based config (decouple)
│   ├── urls.py              # Root URL router + sitemap
│   └── wsgi.py / asgi.py
├── store/                   # Main application
│   ├── models.py            # 10 models (Product, Order, Review, etc.)
│   ├── views.py             # 46 view functions (800+ lines)
│   ├── forms.py             # 10 Django forms with validation
│   ├── admin.py             # Customized admin with fieldsets & filters
│   ├── services.py          # OTP, email, shipping calculation logic
│   ├── payment_services.py  # Payment gateway integration layer
│   ├── sitemaps.py          # Dynamic XML sitemaps
│   ├── context_processors.py# Global template context (cart, categories)
│   ├── templatetags/        # Custom filters (PKR currency, star ratings)
│   ├── templates/store/     # 30 HTML templates
│   └── migrations/          # Database migrations
├── static/                  # CSS, JS, favicon, robots.txt
├── nginx/                   # Nginx reverse proxy config
├── Dockerfile               # Multi-stage production build
├── docker-compose.yml       # Full stack orchestration
├── seed_data.py             # Product & category seeder
├── requirements.txt         # Python dependencies
└── .env.example             # Environment variable template
```

---

## Features

### Storefront & Catalog
- **Dynamic product catalog** with categories, filtering, sorting, and pagination
- **Full-text search** with AJAX autocomplete
- **Product detail pages** with image galleries, size/color variants, and related products
- **Star ratings & reviews** system
- **Wishlist** with AJAX toggle (session-based for guests, DB-backed for users)

### Shopping & Checkout
- **Session-based cart** with real-time quantity updates
- **Multi-step checkout** with form validation
- **Coupon/discount system** — percentage & fixed amount, with usage limits and expiry
- **Dynamic shipping calculator** — rate-based by city/province
- **OTP verification** via WhatsApp Business API before order confirmation

### Payment Gateways
- **Cash on Delivery (COD)** — default, with OTP fraud prevention
- **Credit/Debit Card** — Stripe integration (configurable to HBL/PayMob)
- **EasyPaisa** — Pakistan's leading mobile wallet
- **JazzCash** — Mobile payment gateway with HMAC-SHA256 verification
- All gateways ship in **sandbox/simulation mode** — swap API keys for production

### User Accounts
- Registration, login, logout with Django auth
- **Profile management** — edit name, email, phone
- **Order history** with status tracking
- **Persistent wishlist** synced to account

### Admin Dashboard
- Custom `ModelAdmin` with fieldsets, filters, and search
- Payment method & status tracking in order management
- Export-ready order views with transaction IDs
- Coupon management (auto-validation on code, dates, limits)
- Newsletter subscriber management
- Contact form message inbox

### SEO & Marketing
- **XML Sitemaps** — auto-indexed products, categories, and static pages
- **robots.txt** configured for search engines
- **Google Analytics (GA4)** integration point
- **Meta Pixel** integration point
- **Newsletter subscription** with email capture
- **WhatsApp floating widget** for customer support

### Legal & Compliance
- Privacy Policy, Terms & Conditions, Shipping & Returns pages
- **Cookie consent banner** (GDPR-style)
- Secure session handling, CSRF protection, XSS/clickjacking headers

### Brand Pages
- **Our Story** — artisan narrative
- **Corporate Gifting** — B2B offering page
- **Artisan Initiative** — social impact page
- **FAQ** — collapsible accordion

### Production Infrastructure
- **Dockerized** — multi-stage Dockerfile with Gunicorn
- **Nginx** reverse proxy with static file serving
- **docker-compose** — one-command deployment (web + db + nginx)
- **Production hardening** — HSTS, secure cookies, `X-Frame-Options: DENY`
- **Environment-based config** — zero secrets in codebase

---

## Database Schema

```
Category ──< Product ──< OrderItem >── Order
                │                        │
                ├──< Review              ├── Coupon
                │                        ├── payment_method
                └──< WishlistItem        ├── payment_status
                                         └── payment_transaction_id

ShippingRate (city-based pricing)
ContactMessage (form submissions)
NewsletterSubscriber (email capture)
```

**10 Models:**

| Model | Purpose |
|-------|---------|
| `Category` | Product categories with slugs, images, ordering |
| `Product` | Full product with variants, SEO fields, stock tracking |
| `Order` | Orders with 4 payment methods, 5 payment statuses, OTP verification |
| `OrderItem` | Line items with snapshot pricing |
| `Review` | Star ratings (1-5) with moderation support |
| `WishlistItem` | Per-user product bookmarks |
| `Coupon` | Discount codes — percentage/fixed, with limits & expiry |
| `ShippingRate` | City/province-based delivery pricing |
| `ContactMessage` | Customer inquiries from contact form |
| `NewsletterSubscriber` | Email marketing opt-ins |

---

## Payment Flow

```
┌─────────────┐     ┌──────────┐     ┌────────────────┐     ┌──────────────┐
│  Checkout    │────>│ OTP      │────>│ Payment        │────>│ Order        │
│  Form       │     │ Verify   │     │ Gateway        │     │ Confirmed    │
│             │     │ (WhatsApp)│     │ (if online)    │     │              │
└─────────────┘     └──────────┘     └────────────────┘     └──────────────┘
                                           │
                              ┌─────────────┼─────────────┐
                              │             │             │
                          Stripe      EasyPaisa      JazzCash
                        (Card PSP)   (Mobile Wallet) (Mobile Wallet)
```

- **COD orders** skip the payment gateway — proceed directly after OTP
- **Online payments** redirect to the gateway after OTP verification
- Server-to-server **callbacks** handle asynchronous payment confirmation
- All gateways include **hash verification** for tamper protection

---

## Quick Start

### Prerequisites
- Python 3.11+
- pip

### Local Development

```bash
# Clone the repository
git clone https://github.com/AshfaqueMarfani/warmhookhugs.git
cd warmhookhugs

# Create virtual environment
python -m venv venv
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env            # Edit .env with your values

# Run migrations
python manage.py migrate

# Seed sample data (4 categories, 12 products, 6 shipping rates, 2 coupons)
python seed_data.py
python seed_extra.py

# Create admin user
python manage.py createsuperuser

# Start development server
python manage.py runserver
```

Visit `http://localhost:8000` — the store is ready.  
Admin panel at `http://localhost:8000/admin/`.

### Docker Deployment

```bash
# Build and start all services (Django + PostgreSQL + Nginx)
docker-compose up -d --build

# Run migrations inside the container
docker-compose exec web python manage.py migrate

# Collect static files
docker-compose exec web python manage.py collectstatic --noinput

# Create admin user
docker-compose exec web python manage.py createsuperuser
```

---

## Environment Variables

All configuration is managed via `.env` (see [.env.example](.env.example)):

| Variable | Description | Default |
|----------|-------------|---------|
| `SECRET_KEY` | Django secret key | Dev placeholder |
| `DEBUG` | Debug mode | `True` |
| `ALLOWED_HOSTS` | Comma-separated hosts | `localhost,127.0.0.1` |
| `DATABASE_URL` | PostgreSQL connection string | SQLite |
| `STRIPE_PUBLIC_KEY` | Stripe publishable key | Dummy |
| `STRIPE_SECRET_KEY` | Stripe secret key | Dummy |
| `EASYPAISA_STORE_ID` | EasyPaisa merchant ID | Dummy |
| `JAZZCASH_MERCHANT_ID` | JazzCash merchant ID | Dummy |
| `OTP_PROVIDER` | `console` or `whatsapp` | `console` |
| `EMAIL_BACKEND` | Django email backend | Console |
| `GA4_MEASUREMENT_ID` | Google Analytics 4 ID | Empty |

---

## Design System

The UI follows a **luxury boutique** aesthetic with warm, neutral tones:

| Token | Hex | Usage |
|-------|-----|-------|
| Cream | `#FDF8F0` | Page backgrounds |
| Terracotta | `#C2703E` | Primary accent, CTAs |
| Sage Green | `#8B9E7E` | Success states, badges |
| Beige | `#D4C5A9` | Borders, dividers |
| Charcoal | `#3D3D3D` | Text, dark elements |

**Typography:** Playfair Display (headings) + DM Sans (body) — Google Fonts.

---

## Django Skills Demonstrated

This project showcases proficiency across the full Django ecosystem:

- **Models & ORM** — Complex relationships, custom `save()` overrides, computed properties, UUID primary keys, slug generation
- **Class-based & function-based views** — 46 views handling CRUD, AJAX, file uploads, redirects, and payment callbacks
- **Forms & validation** — Custom form classes with regex validators, choice fields, conditional logic
- **Template engine** — Template inheritance, custom template tags/filters, context processors
- **Admin customization** — Custom fieldsets, list displays, filters, search, readonly fields, inline editing
- **Authentication** — Registration, login, logout, `@login_required`, session management
- **Middleware & security** — CSRF, XSS protection, HSTS, secure cookies, `ALLOWED_HOSTS`
- **Sessions** — Cart persistence, OTP flow state, payment tracking across redirects
- **Services layer** — Business logic separation (OTP delivery, email, shipping, payments)
- **Sitemaps** — Dynamic XML sitemaps for SEO
- **Database migrations** — Schema evolution across 3 migration files
- **Deployment** — Docker multi-stage builds, Gunicorn WSGI, Nginx reverse proxy, environment-based settings
- **Third-party integration** — Stripe, EasyPaisa, JazzCash APIs (with HMAC verification), WhatsApp Business API

---

## Sample Data

The seed scripts populate realistic data for demonstration:

| Data | Count |
|------|-------|
| Categories | 4 (Hug Collection, Warmth & Wear, Home & Hearth, Everyday Elegance) |
| Products | 12 (with descriptions, pricing in PKR, stock levels) |
| Shipping Rates | 6 (Karachi, Lahore, Islamabad, Peshawar, Quetta, rest of Pakistan) |
| Coupons | 2 (`WELCOME10` — 10% off, `EID2026` — Rs. 500 off) |

---

## Screenshots

> *Coming soon — upload product images and capture live screenshots.*

---

## License

This project is built for [Warm Hook Hugs](https://www.instagram.com/warmhookhugs.pk) — a real artisan brand. The codebase is shared for **portfolio and educational purposes**.

---

<p align="center">
  Built with Django & crafted with care 🧶
</p>
