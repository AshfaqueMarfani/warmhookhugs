"""
Warm Hook Hugs — Views (Full Feature Set)
============================================
Storefront, Cart, Checkout, OTP, User Accounts, Reviews,
Wishlist, Coupons, Search, Contact, Legal, Order Tracking,
Newsletter, and Brand Pages.
"""

import random
import logging
from decimal import Decimal

from django.conf import settings
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q, Avg
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator

from .models import (
    Category, Product, Order, OrderItem, Review,
    WishlistItem, Coupon, NewsletterSubscriber, ContactMessage, ShippingRate
)
from .forms import (
    CheckoutForm, OTPForm, ContactForm, ReviewForm, NewsletterForm,
    CouponApplyForm, SearchForm, RegisterForm, LoginForm, ProfileForm
)
from .services import send_otp, generate_otp, send_order_confirmation_email, calculate_shipping, send_contact_confirmation_email
from .payment_services import (
    initiate_payment, verify_payment as verify_gateway_payment,
    get_payment_methods, is_online_payment,
)

logger = logging.getLogger(__name__)

PRODUCTS_PER_PAGE = 12


# ══════════════════════════════════════════════
# HELPER — CART (session-based)
# ══════════════════════════════════════════════
def _get_cart(request):
    return request.session.get('cart', {})

def _save_cart(request, cart):
    request.session['cart'] = cart
    request.session.modified = True

def _cart_details(request):
    cart = _get_cart(request)
    items = []
    total = Decimal('0.00')
    for pid, data in cart.items():
        try:
            product = Product.objects.get(id=int(pid), is_active=True)
            qty = int(data.get('qty', 1))
            line_total = product.price * qty
            items.append({
                'product': product,
                'qty': qty,
                'size': data.get('size', ''),
                'color': data.get('color', ''),
                'line_total': line_total,
            })
            total += line_total
        except Product.DoesNotExist:
            continue
    return items, total


# ══════════════════════════════════════════════
# STOREFRONT
# ══════════════════════════════════════════════
def home(request):
    categories = Category.objects.filter(is_active=True)
    featured = Product.objects.filter(is_featured=True, is_active=True)[:8]
    latest = Product.objects.filter(is_active=True)[:8]
    top_rated = Product.objects.filter(is_active=True, reviews__is_approved=True).annotate(
        avg_rating=Avg('reviews__rating')
    ).order_by('-avg_rating')[:4]
    return render(request, 'store/home.html', {
        'categories': categories,
        'featured_products': featured,
        'latest_products': latest,
        'top_rated_products': top_rated,
    })


def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug, is_active=True)
    products = category.products.filter(is_active=True)

    # Sorting
    sort = request.GET.get('sort', 'newest')
    if sort == 'price_low':
        products = products.order_by('price')
    elif sort == 'price_high':
        products = products.order_by('-price')
    elif sort == 'name':
        products = products.order_by('title')
    elif sort == 'popular':
        products = products.annotate(avg_r=Avg('reviews__rating')).order_by('-avg_r')
    else:
        products = products.order_by('-created_at')

    paginator = Paginator(products, PRODUCTS_PER_PAGE)
    page = request.GET.get('page')
    products = paginator.get_page(page)

    return render(request, 'store/category.html', {
        'category': category,
        'products': products,
        'current_sort': sort,
    })


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    related = Product.objects.filter(
        category=product.category, is_active=True
    ).exclude(id=product.id)[:4]
    sizes = [s.strip() for s in product.available_sizes.split(',') if s.strip()] if product.available_sizes else []
    colors = [c.strip() for c in product.available_colors.split(',') if c.strip()] if product.available_colors else []
    reviews = product.reviews.filter(is_approved=True)[:10]
    review_form = ReviewForm()
    is_wishlisted = False
    if request.user.is_authenticated:
        is_wishlisted = WishlistItem.objects.filter(user=request.user, product=product).exists()
    return render(request, 'store/product_detail.html', {
        'product': product,
        'related_products': related,
        'sizes': sizes,
        'colors': colors,
        'reviews': reviews,
        'review_form': review_form,
        'is_wishlisted': is_wishlisted,
    })


def all_products(request):
    products = Product.objects.filter(is_active=True)
    categories = Category.objects.filter(is_active=True)

    # Category filter
    cat_slug = request.GET.get('category', '')
    if cat_slug:
        products = products.filter(category__slug=cat_slug)

    # Price filter
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')
    if min_price:
        products = products.filter(price__gte=Decimal(min_price))
    if max_price:
        products = products.filter(price__lte=Decimal(max_price))

    # Sorting
    sort = request.GET.get('sort', 'newest')
    if sort == 'price_low':
        products = products.order_by('price')
    elif sort == 'price_high':
        products = products.order_by('-price')
    elif sort == 'name':
        products = products.order_by('title')
    elif sort == 'popular':
        products = products.annotate(avg_r=Avg('reviews__rating')).order_by('-avg_r')
    elif sort == 'sale':
        products = products.filter(compare_at_price__isnull=False).order_by('-created_at')
    else:
        products = products.order_by('-created_at')

    paginator = Paginator(products, PRODUCTS_PER_PAGE)
    page = request.GET.get('page')
    products = paginator.get_page(page)

    return render(request, 'store/all_products.html', {
        'products': products,
        'categories': categories,
        'current_sort': sort,
        'current_category': cat_slug,
    })


# ══════════════════════════════════════════════
# SEARCH
# ══════════════════════════════════════════════
def search(request):
    query = request.GET.get('q', '').strip()
    products = Product.objects.none()
    if query:
        products = Product.objects.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(category__name__icontains=query) |
            Q(yarn_type__icontains=query) |
            Q(available_colors__icontains=query),
            is_active=True
        ).distinct()

    sort = request.GET.get('sort', 'relevance')
    if sort == 'price_low':
        products = products.order_by('price')
    elif sort == 'price_high':
        products = products.order_by('-price')

    paginator = Paginator(products, PRODUCTS_PER_PAGE)
    page = request.GET.get('page')
    products = paginator.get_page(page)

    return render(request, 'store/search.html', {
        'products': products,
        'query': query,
        'result_count': paginator.count,
    })


def search_autocomplete(request):
    """AJAX endpoint for search suggestions."""
    query = request.GET.get('q', '').strip()
    if len(query) < 2:
        return JsonResponse({'results': []})
    products = Product.objects.filter(
        Q(title__icontains=query), is_active=True
    )[:5]
    results = [{'title': p.title, 'url': p.get_absolute_url(), 'price': str(p.price)} for p in products]
    return JsonResponse({'results': results})


# ══════════════════════════════════════════════
# CART
# ══════════════════════════════════════════════
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_active=True)
    cart = _get_cart(request)
    pid = str(product_id)
    size = request.POST.get('size', '')
    color = request.POST.get('color', '')

    if pid in cart:
        cart[pid]['qty'] = cart[pid].get('qty', 1) + 1
    else:
        cart[pid] = {'qty': 1, 'size': size, 'color': color}

    _save_cart(request, cart)
    messages.success(request, f'"{product.title}" added to your bag.')
    return redirect('store:cart')


def update_cart(request, product_id):
    cart = _get_cart(request)
    pid = str(product_id)
    if pid in cart:
        qty = int(request.POST.get('qty', 1))
        if qty > 0:
            cart[pid]['qty'] = qty
        else:
            del cart[pid]
        _save_cart(request, cart)
    return redirect('store:cart')


def remove_from_cart(request, product_id):
    cart = _get_cart(request)
    pid = str(product_id)
    if pid in cart:
        del cart[pid]
        _save_cart(request, cart)
        messages.info(request, 'Item removed from your bag.')
    return redirect('store:cart')


def cart_view(request):
    items, total = _cart_details(request)
    # Calculate shipping for display
    city = request.session.get('shipping_city', 'Karachi')
    shipping_cost, est_days, is_free = calculate_shipping(city, total)
    # Check for applied coupon
    coupon_code = request.session.get('coupon_code', '')
    discount = Decimal('0.00')
    if coupon_code:
        try:
            coupon = Coupon.objects.get(code__iexact=coupon_code)
            discount = coupon.apply_discount(total)
        except Coupon.DoesNotExist:
            pass
    grand_total = total - discount + shipping_cost
    return render(request, 'store/cart.html', {
        'cart_items': items,
        'cart_total': total,
        'shipping_cost': shipping_cost,
        'shipping_est_days': est_days,
        'is_free_shipping': is_free,
        'discount': discount,
        'coupon_code': coupon_code,
        'grand_total': grand_total,
        'coupon_form': CouponApplyForm(initial={'coupon_code': coupon_code}),
    })


# ══════════════════════════════════════════════
# COUPON
# ══════════════════════════════════════════════
def apply_coupon(request):
    if request.method == 'POST':
        code = request.POST.get('coupon_code', '').strip().upper()
        try:
            coupon = Coupon.objects.get(code__iexact=code)
            if coupon.is_valid:
                _, total = _cart_details(request)
                if total < coupon.minimum_order:
                    messages.warning(request, f'Minimum order of PKR {coupon.minimum_order:,.0f} required for this code.')
                else:
                    request.session['coupon_code'] = code
                    discount = coupon.apply_discount(total)
                    messages.success(request, f'Coupon "{code}" applied! You save PKR {discount:,.0f}.')
            else:
                messages.error(request, 'This coupon has expired or is no longer valid.')
        except Coupon.DoesNotExist:
            messages.error(request, 'Invalid coupon code.')
    return redirect('store:cart')


def remove_coupon(request):
    request.session.pop('coupon_code', None)
    messages.info(request, 'Coupon removed.')
    return redirect('store:cart')


# ══════════════════════════════════════════════
# CHECKOUT + OTP
# ══════════════════════════════════════════════
def checkout(request):
    items, total = _cart_details(request)
    if not items:
        messages.warning(request, 'Your bag is empty.')
        return redirect('store:home')

    # Calculate discount
    coupon_code = request.session.get('coupon_code', '')
    discount = Decimal('0.00')
    coupon_obj = None
    if coupon_code:
        try:
            coupon_obj = Coupon.objects.get(code__iexact=coupon_code)
            discount = coupon_obj.apply_discount(total)
        except Coupon.DoesNotExist:
            pass

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            city = form.cleaned_data['city']
            shipping_cost, _, _ = calculate_shipping(city, total - discount)
            grand_total = total - discount + shipping_cost

            payment_method = form.cleaned_data.get('payment_method', 'cod')

            order = Order.objects.create(
                user=request.user if request.user.is_authenticated else None,
                full_name=form.cleaned_data['full_name'],
                email=form.cleaned_data['email'],
                phone=form.cleaned_data['phone'],
                address_line_1=form.cleaned_data['address_line_1'],
                address_line_2=form.cleaned_data.get('address_line_2', ''),
                city=city,
                province=form.cleaned_data.get('province', ''),
                postal_code=form.cleaned_data.get('postal_code', ''),
                note=form.cleaned_data.get('note', ''),
                subtotal=total,
                discount_amount=discount,
                shipping_cost=shipping_cost,
                total=grand_total,
                coupon=coupon_obj,
                payment_method=payment_method,
                payment_status='unpaid',
                status='pending',
            )

            cart = _get_cart(request)
            for pid, data in cart.items():
                try:
                    product = Product.objects.get(id=int(pid), is_active=True)
                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        product_title=product.title,
                        price=product.price,
                        quantity=data.get('qty', 1),
                        size=data.get('size', ''),
                        color=data.get('color', ''),
                    )
                    product.stock = max(0, product.stock - int(data.get('qty', 1)))
                    product.save()
                except Product.DoesNotExist:
                    continue

            # Increment coupon usage
            if coupon_obj:
                coupon_obj.times_used += 1
                coupon_obj.save()

            # ── Online Payment Methods: redirect to gateway ──
            if is_online_payment(payment_method):
                request.session['payment_order_id'] = str(order.order_id)
                result = initiate_payment(order, request)
                if result['success'] and result.get('redirect_url'):
                    return redirect(result['redirect_url'])
                else:
                    messages.error(request, result.get('error', 'Payment initiation failed. Please try again.'))
                    order.payment_status = 'failed'
                    order.save()
                    return redirect('store:checkout')

            # ── COD: proceed to OTP verification ──
            otp_code = generate_otp(settings.OTP_LENGTH)
            request.session['otp_code'] = otp_code
            request.session['otp_order_id'] = str(order.order_id)
            request.session['otp_created'] = timezone.now().isoformat()

            send_otp(order.phone, otp_code, order.short_id)

            messages.info(request, f'A 6-digit verification code has been sent to {order.phone}.')
            return redirect('store:otp_verify')
    else:
        initial = {}
        if request.user.is_authenticated:
            initial = {
                'full_name': f'{request.user.first_name} {request.user.last_name}'.strip(),
                'email': request.user.email,
            }
        form = CheckoutForm(initial=initial)

    shipping_cost, est_days, is_free = calculate_shipping('Karachi', total - discount)
    grand_total = total - discount + shipping_cost

    return render(request, 'store/checkout.html', {
        'form': form,
        'cart_items': items,
        'cart_total': total,
        'discount': discount,
        'coupon_code': coupon_code,
        'shipping_cost': shipping_cost,
        'grand_total': grand_total,
        'payment_methods': get_payment_methods(),
    })


def otp_verify(request):
    order_id = request.session.get('otp_order_id')
    if not order_id:
        messages.error(request, 'No pending order found. Please checkout again.')
        return redirect('store:checkout')

    order = get_object_or_404(Order, order_id=order_id)

    if request.method == 'POST':
        form = OTPForm(request.POST)
        if form.is_valid():
            entered_otp = form.cleaned_data['otp_code']
            stored_otp = request.session.get('otp_code')
            otp_created = request.session.get('otp_created')

            if otp_created:
                from datetime import datetime
                created_time = datetime.fromisoformat(otp_created)
                now = timezone.now()
                if timezone.is_naive(created_time):
                    created_time = timezone.make_aware(created_time)
                if (now - created_time).total_seconds() > settings.OTP_EXPIRY_SECONDS:
                    messages.error(request, 'OTP has expired. Please place your order again.')
                    order.status = 'cancelled'
                    order.save()
                    for key in ['otp_code', 'otp_order_id', 'otp_created']:
                        request.session.pop(key, None)
                    return redirect('store:checkout')

            if entered_otp == stored_otp:
                order.status = 'otp_verified'
                order.save()

                request.session.pop('cart', None)
                request.session.pop('otp_code', None)
                request.session.pop('otp_order_id', None)
                request.session.pop('otp_created', None)
                request.session.pop('coupon_code', None)

                # Send confirmation email
                send_order_confirmation_email(order)

                messages.success(request, 'Order confirmed! Thank you for shopping with Warm Hook Hugs.')
                return redirect('store:order_confirmation', order_id=str(order.order_id))
            else:
                messages.error(request, 'Invalid OTP. Please try again.')
    else:
        form = OTPForm()

    return render(request, 'store/otp_verify.html', {
        'form': form,
        'order': order,
        'phone': order.phone,
    })


def resend_otp(request):
    """Resend OTP for current pending order."""
    order_id = request.session.get('otp_order_id')
    if not order_id:
        return redirect('store:checkout')
    order = get_object_or_404(Order, order_id=order_id)
    otp_code = generate_otp(settings.OTP_LENGTH)
    request.session['otp_code'] = otp_code
    request.session['otp_created'] = timezone.now().isoformat()
    send_otp(order.phone, otp_code, order.short_id)
    messages.info(request, f'New OTP sent to {order.phone}.')
    return redirect('store:otp_verify')


def order_confirmation(request, order_id):
    order = get_object_or_404(Order, order_id=order_id)
    return render(request, 'store/order_confirmation.html', {'order': order})


# ══════════════════════════════════════════════
# PAYMENT CALLBACKS
# ══════════════════════════════════════════════
def payment_success(request):
    """Handle successful payment redirect from any gateway."""
    order_id = request.GET.get('order_id') or request.session.get('payment_order_id')
    if not order_id:
        messages.error(request, 'No order found for this payment.')
        return redirect('store:home')

    order = get_object_or_404(Order, order_id=order_id)

    # Verify payment with gateway
    result = verify_gateway_payment(order.payment_method, request)

    if result['success']:
        order.payment_status = 'paid'
        order.payment_transaction_id = result.get('transaction_id', '')
        order.status = 'otp_verified'  # Skip OTP for paid orders
        order.save()

        # Clear cart & session
        request.session.pop('cart', None)
        request.session.pop('coupon_code', None)
        request.session.pop('payment_order_id', None)

        # Send confirmation email
        send_order_confirmation_email(order)

        messages.success(request, 'Payment successful! Your order has been confirmed.')
        return redirect('store:order_confirmation', order_id=str(order.order_id))
    else:
        order.payment_status = 'failed'
        order.save()
        messages.error(request, f'Payment verification failed: {result.get("error", "Unknown error")}. Please contact support.')
        return redirect('store:payment_failed', order_id=str(order.order_id))


def payment_cancel(request):
    """Handle cancelled payment from gateway."""
    order_id = request.GET.get('order_id') or request.session.get('payment_order_id')
    if order_id:
        try:
            order = Order.objects.get(order_id=order_id)
            order.payment_status = 'failed'
            order.status = 'cancelled'
            order.save()
        except Order.DoesNotExist:
            pass
        request.session.pop('payment_order_id', None)

    messages.warning(request, 'Payment was cancelled. You can try again or choose a different payment method.')
    return redirect('store:checkout')


def payment_failed(request, order_id):
    """Show payment failure page with retry option."""
    order = get_object_or_404(Order, order_id=order_id)
    return render(request, 'store/payment_failed.html', {'order': order})


def payment_callback_easypaisa(request):
    """EasyPaisa server-to-server callback."""
    order_ref = request.POST.get('orderRefNum') or request.GET.get('orderRefNum', '')
    if not order_ref:
        return JsonResponse({'status': 'error', 'message': 'Missing order reference'})

    try:
        order = Order.objects.get(order_id=order_ref)
    except Order.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Order not found'})

    result = verify_gateway_payment('easypaisa', request)
    if result['success']:
        order.payment_status = 'paid'
        order.payment_transaction_id = result.get('transaction_id', '')
        order.status = 'otp_verified'
        order.save()
        send_order_confirmation_email(order)
    else:
        order.payment_status = 'failed'
        order.save()

    return JsonResponse({'status': 'ok'})


def payment_callback_jazzcash(request):
    """JazzCash server-to-server callback."""
    bill_ref = request.POST.get('pp_BillReference', '')
    if not bill_ref:
        return JsonResponse({'status': 'error', 'message': 'Missing bill reference'})

    try:
        order = Order.objects.get(order_id__startswith=bill_ref)
    except Order.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Order not found'})

    result = verify_gateway_payment('jazzcash', request)
    if result['success']:
        order.payment_status = 'paid'
        order.payment_transaction_id = result.get('transaction_id', '')
        order.status = 'otp_verified'
        order.save()
        send_order_confirmation_email(order)
    else:
        order.payment_status = 'failed'
        order.save()

    return JsonResponse({'status': 'ok'})


# ══════════════════════════════════════════════
# ORDER TRACKING
# ══════════════════════════════════════════════
def track_order(request):
    order = None
    if request.method == 'POST' or request.GET.get('order_id'):
        oid = request.POST.get('order_id', '') or request.GET.get('order_id', '')
        phone = request.POST.get('phone', '') or request.GET.get('phone', '')
        if oid and phone:
            phone_clean = phone.replace('-', '').replace(' ', '')
            try:
                order = Order.objects.get(
                    Q(order_id__startswith=oid.lower()) | Q(order_id=oid),
                    phone__endswith=phone_clean[-7:]
                )
            except (Order.DoesNotExist, ValueError):
                messages.error(request, 'Order not found. Please check your Order ID and phone number.')
    return render(request, 'store/track_order.html', {'order': order})


# ══════════════════════════════════════════════
# PRODUCT REVIEWS
# ══════════════════════════════════════════════
def submit_review(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_active=True)
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            # Check for duplicate
            email = form.cleaned_data['email']
            if Review.objects.filter(product=product, email=email).exists():
                messages.warning(request, 'You have already reviewed this product.')
            else:
                review = Review.objects.create(
                    product=product,
                    user=request.user if request.user.is_authenticated else None,
                    name=form.cleaned_data['name'],
                    email=email,
                    rating=form.cleaned_data['rating'],
                    title=form.cleaned_data.get('title', ''),
                    comment=form.cleaned_data['comment'],
                    is_approved=False,  # Requires admin approval
                )
                messages.success(request, 'Thank you! Your review will appear after approval.')
        else:
            messages.error(request, 'Please fill all required fields and select a rating.')
    return redirect('store:product_detail', slug=product.slug)


# ══════════════════════════════════════════════
# WISHLIST
# ══════════════════════════════════════════════
@login_required
def wishlist_view(request):
    items = WishlistItem.objects.filter(user=request.user).select_related('product', 'product__category')
    return render(request, 'store/wishlist.html', {'wishlist_items': items})


@login_required
def wishlist_toggle(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_active=True)
    item, created = WishlistItem.objects.get_or_create(user=request.user, product=product)
    if not created:
        item.delete()
        messages.info(request, f'"{product.title}" removed from wishlist.')
    else:
        messages.success(request, f'"{product.title}" added to your wishlist.')

    # AJAX response
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'wishlisted': created, 'count': request.user.wishlist.count()})

    next_url = request.POST.get('next', request.META.get('HTTP_REFERER', '/'))
    return redirect(next_url)


# ══════════════════════════════════════════════
# NEWSLETTER
# ══════════════════════════════════════════════
def newsletter_subscribe(request):
    if request.method == 'POST':
        form = NewsletterForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            name = form.cleaned_data.get('name', '')
            sub, created = NewsletterSubscriber.objects.get_or_create(
                email=email,
                defaults={'name': name}
            )
            if created:
                messages.success(request, 'Welcome! You\'re now subscribed to our newsletter.')
            else:
                messages.info(request, 'You\'re already subscribed!')
        else:
            messages.error(request, 'Please enter a valid email address.')

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True})

    return redirect(request.META.get('HTTP_REFERER', '/'))


# ══════════════════════════════════════════════
# CONTACT
# ══════════════════════════════════════════════
def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            ContactMessage.objects.create(
                name=form.cleaned_data['name'],
                email=form.cleaned_data['email'],
                phone=form.cleaned_data.get('phone', ''),
                subject=form.cleaned_data['subject'],
                order_id=form.cleaned_data.get('order_id', ''),
                message=form.cleaned_data['message'],
            )
            # Send auto-reply
            send_contact_confirmation_email(form.cleaned_data['name'], form.cleaned_data['email'])
            messages.success(request, 'Thank you! We\'ve received your message and will respond within 24-48 hours.')
            return redirect('store:contact')
    else:
        form = ContactForm()
    return render(request, 'store/contact.html', {'form': form})


# ══════════════════════════════════════════════
# USER ACCOUNTS
# ══════════════════════════════════════════════
def register_view(request):
    if request.user.is_authenticated:
        return redirect('store:account')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Welcome to Warm Hook Hugs, {user.first_name}!')
            return redirect('store:account')
    else:
        form = RegisterForm()
    return render(request, 'store/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('store:account')
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, {user.first_name or user.username}!')
            next_url = request.GET.get('next', 'store:account')
            return redirect(next_url)
    else:
        form = LoginForm()
    return render(request, 'store/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('store:home')


@login_required
def account_view(request):
    orders = Order.objects.filter(user=request.user).exclude(status='pending')[:10]
    wishlist_count = WishlistItem.objects.filter(user=request.user).count()
    return render(request, 'store/account.html', {
        'orders': orders,
        'wishlist_count': wishlist_count,
    })


@login_required
def account_orders(request):
    orders = Order.objects.filter(user=request.user).exclude(status='pending')
    paginator = Paginator(orders, 10)
    page = request.GET.get('page')
    orders = paginator.get_page(page)
    return render(request, 'store/account_orders.html', {'orders': orders})


@login_required
def profile_edit(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST)
        if form.is_valid():
            request.user.first_name = form.cleaned_data['first_name']
            request.user.last_name = form.cleaned_data.get('last_name', '')
            request.user.email = form.cleaned_data['email']
            request.user.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('store:account')
    else:
        form = ProfileForm(initial={
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'email': request.user.email,
        })
    return render(request, 'store/profile_edit.html', {'form': form})


# ══════════════════════════════════════════════
# SHIPPING CALCULATOR (AJAX)
# ══════════════════════════════════════════════
def calculate_shipping_ajax(request):
    city = request.GET.get('city', 'Karachi')
    _, total = _cart_details(request)
    cost, days, is_free = calculate_shipping(city, total)
    request.session['shipping_city'] = city
    return JsonResponse({
        'cost': str(cost),
        'days': days,
        'is_free': is_free,
    })


# ══════════════════════════════════════════════
# LEGAL PAGES
# ══════════════════════════════════════════════
def privacy_policy(request):
    return render(request, 'store/privacy_policy.html')

def terms_conditions(request):
    return render(request, 'store/terms_conditions.html')

def shipping_returns(request):
    rates = ShippingRate.objects.filter(is_active=True).exclude(city__iexact='default')
    return render(request, 'store/shipping_returns.html', {'shipping_rates': rates})

def faq(request):
    return render(request, 'store/faq.html')


# ══════════════════════════════════════════════
# BRAND / CONTENT PAGES
# ══════════════════════════════════════════════
def our_story(request):
    return render(request, 'store/our_story.html')

def corporate_gifting(request):
    return render(request, 'store/corporate_gifting.html')

def artisan_initiative(request):
    return render(request, 'store/artisan_initiative.html')


# ══════════════════════════════════════════════
# ERROR HANDLERS
# ══════════════════════════════════════════════
def handler404(request, exception):
    return render(request, 'store/404.html', status=404)

def handler500(request):
    return render(request, 'store/500.html', status=500)