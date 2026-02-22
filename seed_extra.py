"""
Warm Hook Hugs — Supplementary Seed (Shipping Rates + Coupons)
Run: python seed_extra.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from store.models import ShippingRate, Coupon
from decimal import Decimal
from django.utils import timezone
from datetime import timedelta

print("Seeding shipping rates...")
rates = [
    ('Karachi', Decimal('150'), Decimal('3000'), '2-3 business days'),
    ('Lahore', Decimal('200'), Decimal('4000'), '3-5 business days'),
    ('Islamabad', Decimal('200'), Decimal('4000'), '3-5 business days'),
    ('Rawalpindi', Decimal('200'), Decimal('4000'), '3-5 business days'),
    ('Faisalabad', Decimal('250'), Decimal('5000'), '4-6 business days'),
    ('default', Decimal('250'), Decimal('5000'), '5-7 business days'),
]
for city, rate, free_above, days in rates:
    obj, created = ShippingRate.objects.get_or_create(
        city=city,
        defaults={'rate': rate, 'free_above': free_above, 'estimated_days': days, 'is_active': True}
    )
    status = "created" if created else "exists"
    print(f"  ShippingRate: {city} - {status}")

print("\nSeeding coupons...")
coupon, created = Coupon.objects.get_or_create(
    code='WELCOME10',
    defaults={
        'discount_type': 'percentage',
        'discount_value': Decimal('10'),
        'minimum_order': Decimal('1500'),
        'max_uses': 1000,
        'times_used': 0,
        'valid_from': timezone.now(),
        'valid_until': timezone.now() + timedelta(days=365),
        'is_active': True,
    }
)
status = "created" if created else "exists"
print(f"  Coupon WELCOME10: {status}")

coupon2, created = Coupon.objects.get_or_create(
    code='EID2026',
    defaults={
        'discount_type': 'percentage',
        'discount_value': Decimal('15'),
        'minimum_order': Decimal('2000'),
        'max_uses': 500,
        'times_used': 0,
        'valid_from': timezone.now(),
        'valid_until': timezone.now() + timedelta(days=180),
        'is_active': True,
    }
)
status = "created" if created else "exists"
print(f"  Coupon EID2026: {status}")

print("\nDone! Shipping rates and coupons seeded.")
