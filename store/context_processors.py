"""
Warm Hook Hugs — Context Processors
=====================================
Global template variables for cart, wishlist, newsletter, SEO.
"""
from .forms import NewsletterForm, SearchForm


def cart_item_count(request):
    cart = request.session.get('cart', {})
    count = sum(item.get('qty', 1) for item in cart.values())
    return {'cart_count': count}


def wishlist_count(request):
    if request.user.is_authenticated:
        return {'wishlist_count': request.user.wishlist.count()}
    return {'wishlist_count': 0}


def global_forms(request):
    return {
        'newsletter_form': NewsletterForm(),
        'search_form': SearchForm(request.GET),
    }


def site_settings(request):
    return {
        'brand_name': 'Warm Hook Hugs',
        'brand_tagline': 'Woven with Intention. Crafted for Generations.',
        'brand_phone': '+92 300 1234567',
        'brand_email': 'hello@warmhookhugs.pk',
        'brand_instagram': 'https://www.instagram.com/warmhookhugs.pk',
        'brand_whatsapp': 'https://wa.me/923001234567',
        'brand_address': 'Karachi, Pakistan',
        'current_year': '2026',
    }
