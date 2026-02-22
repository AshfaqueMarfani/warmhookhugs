"""
Warm Hook Hugs — XML Sitemaps
================================
"""

from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import Product, Category


class ProductSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.8

    def items(self):
        return Product.objects.filter(is_active=True)

    def lastmod(self, obj):
        return obj.updated_at


class CategorySitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.7

    def items(self):
        return Category.objects.filter(is_active=True)

    def lastmod(self, obj):
        return obj.updated_at


class StaticViewSitemap(Sitemap):
    changefreq = 'monthly'
    priority = 0.5

    def items(self):
        return [
            'store:home', 'store:all_products', 'store:our_story',
            'store:corporate_gifting', 'store:artisan_initiative',
            'store:contact', 'store:faq', 'store:shipping_returns',
            'store:privacy_policy', 'store:terms_conditions',
        ]

    def location(self, item):
        return reverse(item)
