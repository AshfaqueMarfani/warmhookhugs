"""
Warm Hook Hugs — Services
============================
WhatsApp OTP, SMS, Email notifications, Shipping calculator.
"""

import random
import logging
import requests
from decimal import Decimal

from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

logger = logging.getLogger(__name__)


# ══════════════════════════════════════════════
# OTP SERVICE (WhatsApp / SMS / Console)
# ══════════════════════════════════════════════
def generate_otp(length=6):
    """Generate a random numeric OTP."""
    return ''.join([str(random.randint(0, 9)) for _ in range(length)])


def send_otp_whatsapp(phone, otp_code, order_short_id=''):
    """
    Send OTP via WhatsApp Business API (Meta Cloud API).
    Uses dummy credentials — replace with real ones before launch.
    
    Meta WhatsApp Cloud API docs:
    https://developers.facebook.com/docs/whatsapp/cloud-api/
    """
    # Configuration from settings
    wa_phone_id = getattr(settings, 'WHATSAPP_PHONE_NUMBER_ID', 'DUMMY_PHONE_ID_123456')
    wa_token = getattr(settings, 'WHATSAPP_ACCESS_TOKEN', 'DUMMY_ACCESS_TOKEN_REPLACE_ME')
    wa_api_version = getattr(settings, 'WHATSAPP_API_VERSION', 'v18.0')
    
    # Format phone number (ensure +92 prefix for Pakistan)
    formatted_phone = phone.replace('-', '').replace(' ', '')
    if formatted_phone.startswith('0'):
        formatted_phone = '92' + formatted_phone[1:]
    elif not formatted_phone.startswith('92') and not formatted_phone.startswith('+92'):
        formatted_phone = '92' + formatted_phone
    formatted_phone = formatted_phone.replace('+', '')
    
    url = f"https://graph.facebook.com/{wa_api_version}/{wa_phone_id}/messages"
    
    headers = {
        'Authorization': f'Bearer {wa_token}',
        'Content-Type': 'application/json',
    }
    
    # Message payload — using a text message (or use template for production)
    payload = {
        "messaging_product": "whatsapp",
        "to": formatted_phone,
        "type": "text",
        "text": {
            "body": (
                f"🧶 *Warm Hook Hugs* — Order Verification\n\n"
                f"Your OTP code is: *{otp_code}*\n\n"
                f"{'Order: ' + order_short_id + chr(10) if order_short_id else ''}"
                f"This code expires in 5 minutes.\n"
                f"Do not share this code with anyone.\n\n"
                f"Thank you for shopping with us! 💕"
            )
        }
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        if response.status_code in (200, 201):
            logger.info(f"[WhatsApp OTP] Sent to {formatted_phone} for order {order_short_id}")
            return True
        else:
            logger.warning(
                f"[WhatsApp OTP] Failed for {formatted_phone}: "
                f"{response.status_code} — {response.text}"
            )
            # Fall back to console simulation
            _simulate_otp(phone, otp_code, order_short_id)
            return False
    except requests.RequestException as e:
        logger.error(f"[WhatsApp OTP] Network error: {e}")
        # Fall back to console simulation
        _simulate_otp(phone, otp_code, order_short_id)
        return False


def _simulate_otp(phone, otp_code, order_short_id=''):
    """Simulate OTP delivery by printing to console (dev/fallback)."""
    logger.info(f"[OTP SIMULATION] Code {otp_code} → {phone} (Order: {order_short_id})")
    print(f"\n{'='*55}")
    print(f"  📱 WhatsApp OTP for {phone}: {otp_code}")
    print(f"  Order: {order_short_id}")
    print(f"  (Simulated — WhatsApp API not configured)")
    print(f"{'='*55}\n")


def send_otp(phone, otp_code, order_short_id=''):
    """
    Main OTP dispatcher. Tries WhatsApp first, falls back to console.
    """
    provider = getattr(settings, 'OTP_PROVIDER', 'console')
    
    if provider == 'whatsapp':
        return send_otp_whatsapp(phone, otp_code, order_short_id)
    else:
        # Console simulation (development)
        _simulate_otp(phone, otp_code, order_short_id)
        return True


# ══════════════════════════════════════════════
# EMAIL NOTIFICATION SERVICE
# ══════════════════════════════════════════════
def send_order_confirmation_email(order):
    """Send order confirmation email to customer."""
    if not order.email:
        return False
    
    subject = f"Order Confirmed — {order.short_id} | Warm Hook Hugs"
    
    context = {
        'order': order,
        'items': order.items.all(),
    }
    
    try:
        html_message = render_to_string('store/emails/order_confirmation.html', context)
        plain_message = strip_tags(html_message)
        
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[order.email],
            html_message=html_message,
            fail_silently=True,
        )
        logger.info(f"[Email] Order confirmation sent to {order.email} for {order.short_id}")
        return True
    except Exception as e:
        logger.error(f"[Email] Failed to send confirmation: {e}")
        return False


def send_order_shipped_email(order):
    """Send shipping notification email."""
    if not order.email:
        return False
    
    subject = f"Your Order Has Shipped! — {order.short_id} | Warm Hook Hugs"
    
    context = {
        'order': order,
        'tracking_number': order.tracking_number,
        'tracking_url': order.tracking_url,
    }
    
    try:
        html_message = render_to_string('store/emails/order_shipped.html', context)
        plain_message = strip_tags(html_message)
        
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[order.email],
            html_message=html_message,
            fail_silently=True,
        )
        logger.info(f"[Email] Shipping notification sent for {order.short_id}")
        return True
    except Exception as e:
        logger.error(f"[Email] Failed to send shipping notification: {e}")
        return False


def send_contact_confirmation_email(name, email):
    """Send auto-reply for contact form submissions."""
    subject = "We've Received Your Message | Warm Hook Hugs"
    
    message = (
        f"Dear {name},\n\n"
        f"Thank you for reaching out to Warm Hook Hugs!\n\n"
        f"We've received your message and will get back to you within 24-48 hours.\n"
        f"For urgent inquiries, message us on WhatsApp or Instagram @warmhookhugs.pk.\n\n"
        f"Warm regards,\n"
        f"The Warm Hook Hugs Team\n"
        f"🧶 Woven with Intention. Crafted for Generations."
    )
    
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=True,
        )
        return True
    except Exception:
        return False


# ══════════════════════════════════════════════
# SHIPPING CALCULATOR
# ══════════════════════════════════════════════
def calculate_shipping(city, subtotal):
    """
    Calculate shipping cost based on city and order subtotal.
    Returns (shipping_cost, estimated_days, is_free)
    """
    from .models import ShippingRate
    
    # Try exact city match
    try:
        rate = ShippingRate.objects.get(city__iexact=city.strip(), is_active=True)
    except ShippingRate.DoesNotExist:
        # Fall back to default rate
        try:
            rate = ShippingRate.objects.get(city__iexact='default', is_active=True)
        except ShippingRate.DoesNotExist:
            # Hardcoded fallback
            if subtotal >= Decimal('5000'):
                return Decimal('0'), '3-5 business days', True
            return Decimal('250'), '3-5 business days', False
    
    if subtotal >= rate.free_above:
        return Decimal('0'), rate.estimated_days, True
    
    return rate.rate, rate.estimated_days, False
