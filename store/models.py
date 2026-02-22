"""
Warm Hook Hugs — Data Models
==============================
Category, Product, Order, OrderItem, Review, Wishlist, Coupon,
Newsletter, ContactMessage

All prices are in PKR. The only V1 payment method is Cash on Delivery (COD)
with mandatory OTP verification to prevent fake/bogus orders.
"""

import uuid
from decimal import Decimal
from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.utils import timezone
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


# ──────────────────────────────────────────────
# CATEGORY
# ──────────────────────────────────────────────
class Category(models.Model):
    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    description = models.TextField(blank=True)
    meta_title = models.CharField(max_length=70, blank=True, help_text="SEO title (max 70 chars)")
    meta_description = models.CharField(max_length=160, blank=True, help_text="SEO description (max 160 chars)")
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    display_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['display_order', 'name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('store:category_detail', args=[self.slug])

    @property
    def active_products_count(self):
        return self.products.filter(is_active=True).count()


# ──────────────────────────────────────────────
# PRODUCT
# ──────────────────────────────────────────────
class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    title = models.CharField(max_length=300)
    slug = models.SlugField(max_length=300, unique=True, blank=True)
    description = models.TextField(help_text="Premium product description.")
    short_description = models.CharField(max_length=300, blank=True, help_text="One-liner for cards/SEO.")
    meta_title = models.CharField(max_length=70, blank=True, help_text="SEO title")
    meta_description = models.CharField(max_length=160, blank=True, help_text="SEO description")
    price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Price in PKR.")
    compare_at_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, help_text="Internal cost for margin tracking.")
    stock = models.PositiveIntegerField(default=0)
    sku = models.CharField(max_length=50, blank=True, unique=True, null=True, help_text="Stock Keeping Unit")
    weight = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True, help_text="Weight in grams for shipping calc.")
    image = models.ImageField(upload_to='products/')
    image_alt = models.ImageField(upload_to='products/', blank=True, null=True)
    image_3 = models.ImageField(upload_to='products/', blank=True, null=True, help_text="Third product image")
    image_4 = models.ImageField(upload_to='products/', blank=True, null=True, help_text="Fourth product image")
    yarn_type = models.CharField(max_length=100, blank=True)
    available_sizes = models.CharField(max_length=200, blank=True)
    available_colors = models.CharField(max_length=300, blank=True)
    care_instructions = models.TextField(blank=True, help_text="Washing/care details.")
    is_featured = models.BooleanField(default=False, help_text="Show on homepage.")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('store:product_detail', args=[self.slug])

    @property
    def in_stock(self):
        return self.stock > 0

    @property
    def is_on_sale(self):
        return self.compare_at_price and self.compare_at_price > self.price

    @property
    def discount_percentage(self):
        if self.is_on_sale:
            return int(((self.compare_at_price - self.price) / self.compare_at_price) * 100)
        return 0

    @property
    def avg_rating(self):
        reviews = self.reviews.filter(is_approved=True)
        if reviews.exists():
            return round(reviews.aggregate(models.Avg('rating'))['rating__avg'], 1)
        return 0

    @property
    def review_count(self):
        return self.reviews.filter(is_approved=True).count()

    def get_all_images(self):
        imgs = []
        if self.image:
            imgs.append(self.image)
        if self.image_alt:
            imgs.append(self.image_alt)
        if self.image_3:
            imgs.append(self.image_3)
        if self.image_4:
            imgs.append(self.image_4)
        return imgs


# ──────────────────────────────────────────────
# ORDER
# ──────────────────────────────────────────────
class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('otp_verified', 'OTP Verified'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]

    PAYMENT_METHOD_CHOICES = [
        ('cod', 'Cash on Delivery'),
        ('card', 'Credit / Debit Card'),
        ('easypaisa', 'EasyPaisa'),
        ('jazzcash', 'JazzCash'),
    ]

    PAYMENT_STATUS_CHOICES = [
        ('unpaid', 'Unpaid'),
        ('pending', 'Payment Pending'),
        ('paid', 'Paid'),
        ('failed', 'Payment Failed'),
        ('refunded', 'Refunded'),
    ]

    order_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    full_name = models.CharField(max_length=200)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20)
    address_line_1 = models.CharField(max_length=300)
    address_line_2 = models.CharField(max_length=300, blank=True)
    city = models.CharField(max_length=100)
    province = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=10, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='cod')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='unpaid')
    payment_transaction_id = models.CharField(max_length=200, blank=True, help_text="Gateway transaction/reference ID")
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    coupon = models.ForeignKey('Coupon', on_delete=models.SET_NULL, null=True, blank=True)
    note = models.TextField(blank=True)
    tracking_number = models.CharField(max_length=100, blank=True, help_text="Courier tracking number")
    tracking_url = models.URLField(blank=True, help_text="Direct tracking URL")
    shipped_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Order {self.short_id} — {self.full_name} — {self.get_status_display()}"

    def get_absolute_url(self):
        return reverse('store:order_confirmation', args=[str(self.order_id)])

    @property
    def short_id(self):
        return str(self.order_id)[:8].upper()

    @property
    def payment_method_display_short(self):
        icons = {'cod': '💰', 'card': '💳', 'easypaisa': '📱', 'jazzcash': '📱'}
        return f"{icons.get(self.payment_method, '')} {self.get_payment_method_display()}"

    @property
    def is_online_payment(self):
        return self.payment_method in ('card', 'easypaisa', 'jazzcash')

    def save(self, *args, **kwargs):
        # Auto-set timestamps on status change
        if self.status == 'shipped' and not self.shipped_at:
            self.shipped_at = timezone.now()
        if self.status == 'delivered' and not self.delivered_at:
            self.delivered_at = timezone.now()
        if self.payment_status == 'paid' and not self.paid_at:
            self.paid_at = timezone.now()
        super().save(*args, **kwargs)


# ──────────────────────────────────────────────
# ORDER ITEM
# ──────────────────────────────────────────────
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    product_title = models.CharField(max_length=300)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    size = models.CharField(max_length=50, blank=True)
    color = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return f"{self.quantity}× {self.product_title}"

    @property
    def line_total(self):
        return self.price * self.quantity


# ──────────────────────────────────────────────
# PRODUCT REVIEW
# ──────────────────────────────────────────────
class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=100, help_text="Reviewer display name")
    email = models.EmailField(blank=True)
    rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Rating 1-5 stars"
    )
    title = models.CharField(max_length=200, blank=True)
    comment = models.TextField()
    is_approved = models.BooleanField(default=False, help_text="Must be approved before showing.")
    is_verified_purchase = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ['product', 'email']  # One review per email per product

    def __str__(self):
        return f"{self.name} — {self.rating}★ — {self.product.title[:30]}"


# ──────────────────────────────────────────────
# WISHLIST
# ──────────────────────────────────────────────
class WishlistItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wishlist')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='wishlisted_by')
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'product']
        ordering = ['-added_at']

    def __str__(self):
        return f"{self.user.username} ♥ {self.product.title}"


# ──────────────────────────────────────────────
# COUPON / DISCOUNT CODE
# ──────────────────────────────────────────────
class Coupon(models.Model):
    DISCOUNT_TYPE_CHOICES = [
        ('percentage', 'Percentage Off'),
        ('fixed', 'Fixed Amount Off (PKR)'),
    ]

    code = models.CharField(max_length=30, unique=True)
    description = models.CharField(max_length=200, blank=True)
    discount_type = models.CharField(max_length=10, choices=DISCOUNT_TYPE_CHOICES, default='percentage')
    discount_value = models.DecimalField(max_digits=10, decimal_places=2, help_text="Percentage or fixed PKR amount")
    minimum_order = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Minimum order total to use this coupon")
    max_uses = models.PositiveIntegerField(default=0, help_text="0 = unlimited")
    times_used = models.PositiveIntegerField(default=0)
    valid_from = models.DateTimeField(default=timezone.now)
    valid_until = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.code} — {self.get_discount_type_display()}: {self.discount_value}"

    @property
    def is_valid(self):
        now = timezone.now()
        if not self.is_active:
            return False
        if self.valid_until and now > self.valid_until:
            return False
        if now < self.valid_from:
            return False
        if self.max_uses > 0 and self.times_used >= self.max_uses:
            return False
        return True

    def apply_discount(self, subtotal):
        if not self.is_valid:
            return Decimal('0.00')
        if subtotal < self.minimum_order:
            return Decimal('0.00')
        if self.discount_type == 'percentage':
            discount = (subtotal * self.discount_value) / Decimal('100')
        else:
            discount = self.discount_value
        return min(discount, subtotal)


# ──────────────────────────────────────────────
# NEWSLETTER SUBSCRIBER
# ──────────────────────────────────────────────
class NewsletterSubscriber(models.Model):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-subscribed_at']

    def __str__(self):
        return self.email


# ──────────────────────────────────────────────
# CONTACT MESSAGE
# ──────────────────────────────────────────────
class ContactMessage(models.Model):
    SUBJECT_CHOICES = [
        ('general', 'General Inquiry'),
        ('order', 'Order Support'),
        ('custom', 'Custom Order Request'),
        ('wholesale', 'Wholesale / B2B'),
        ('feedback', 'Feedback'),
        ('other', 'Other'),
    ]

    name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    subject = models.CharField(max_length=20, choices=SUBJECT_CHOICES, default='general')
    message = models.TextField()
    order_id = models.CharField(max_length=50, blank=True, help_text="Related order ID if applicable")
    is_read = models.BooleanField(default=False)
    is_resolved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} — {self.get_subject_display()} — {'✓' if self.is_resolved else '○'}"


# ──────────────────────────────────────────────
# SHIPPING RATE
# ──────────────────────────────────────────────
class ShippingRate(models.Model):
    city = models.CharField(max_length=100, unique=True, help_text="City name (or 'default' for fallback)")
    rate = models.DecimalField(max_digits=8, decimal_places=2, help_text="Shipping cost in PKR")
    free_above = models.DecimalField(max_digits=10, decimal_places=2, default=5000, help_text="Free shipping above this total")
    estimated_days = models.CharField(max_length=20, default='3-5 business days')
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['city']

    def __str__(self):
        return f"{self.city}: PKR {self.rate} (free above PKR {self.free_above})"
