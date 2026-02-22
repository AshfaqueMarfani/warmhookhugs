"""
Warm Hook Hugs — Store URL Configuration (Full Feature Set)
=============================================================
"""

from django.urls import path
from . import views

app_name = 'store'

urlpatterns = [
    # ── Storefront ──
    path('', views.home, name='home'),
    path('shop/', views.all_products, name='all_products'),
    path('category/<slug:slug>/', views.category_detail, name='category_detail'),
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),
    path('search/', views.search, name='search'),
    path('search/autocomplete/', views.search_autocomplete, name='search_autocomplete'),

    # ── Cart ──
    path('cart/', views.cart_view, name='cart'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/<int:product_id>/', views.update_cart, name='update_cart'),
    path('cart/remove/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),

    # ── Coupon ──
    path('cart/apply-coupon/', views.apply_coupon, name='apply_coupon'),
    path('cart/remove-coupon/', views.remove_coupon, name='remove_coupon'),

    # ── Checkout & OTP ──
    path('checkout/', views.checkout, name='checkout'),
    path('verify-otp/', views.otp_verify, name='otp_verify'),
    path('resend-otp/', views.resend_otp, name='resend_otp'),
    path('order/<uuid:order_id>/confirmed/', views.order_confirmation, name='order_confirmation'),

    # ── Payment Callbacks ──
    path('payment/success/', views.payment_success, name='payment_success'),
    path('payment/cancel/', views.payment_cancel, name='payment_cancel'),
    path('payment/<uuid:order_id>/failed/', views.payment_failed, name='payment_failed'),
    path('payment/callback/easypaisa/', views.payment_callback_easypaisa, name='payment_callback_easypaisa'),
    path('payment/callback/jazzcash/', views.payment_callback_jazzcash, name='payment_callback_jazzcash'),

    # ── Order Tracking ──
    path('track-order/', views.track_order, name='track_order'),

    # ── Reviews ──
    path('review/<int:product_id>/', views.submit_review, name='submit_review'),

    # ── Wishlist ──
    path('wishlist/', views.wishlist_view, name='wishlist'),
    path('wishlist/toggle/<int:product_id>/', views.wishlist_toggle, name='wishlist_toggle'),

    # ── Newsletter ──
    path('newsletter/subscribe/', views.newsletter_subscribe, name='newsletter_subscribe'),

    # ── User Accounts ──
    path('account/', views.account_view, name='account'),
    path('account/orders/', views.account_orders, name='account_orders'),
    path('account/profile/', views.profile_edit, name='profile_edit'),
    path('account/register/', views.register_view, name='register'),
    path('account/login/', views.login_view, name='login'),
    path('account/logout/', views.logout_view, name='logout'),

    # ── Contact ──
    path('contact/', views.contact, name='contact'),

    # ── Shipping Calculator (AJAX) ──
    path('shipping/calculate/', views.calculate_shipping_ajax, name='calculate_shipping'),

    # ── Legal Pages ──
    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
    path('terms-conditions/', views.terms_conditions, name='terms_conditions'),
    path('shipping-returns/', views.shipping_returns, name='shipping_returns'),
    path('faq/', views.faq, name='faq'),

    # ── Brand Pages ──
    path('our-story/', views.our_story, name='our_story'),
    path('corporate-gifting/', views.corporate_gifting, name='corporate_gifting'),
    path('artisan-initiative/', views.artisan_initiative, name='artisan_initiative'),
]
