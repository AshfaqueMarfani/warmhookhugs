"""
Warm Hook Hugs — Admin Configuration (Full Feature Set)
=========================================================
"""

from django.contrib import admin
from .models import (
    Category, Product, Order, OrderItem, Review,
    WishlistItem, Coupon, NewsletterSubscriber, ContactMessage, ShippingRate
)

admin.site.site_header = 'Warm Hook Hugs — Management'
admin.site.site_title = 'WHH Admin'
admin.site.index_title = 'Dashboard'


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_active', 'display_order', 'product_count', 'created_at')
    list_editable = ('is_active', 'display_order')
    list_filter = ('is_active',)
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}

    def product_count(self, obj):
        return obj.products.count()
    product_count.short_description = 'Products'


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'price', 'stock', 'sku', 'avg_rating_display', 'is_featured', 'is_active', 'created_at')
    list_editable = ('price', 'stock', 'is_featured', 'is_active')
    list_filter = ('category', 'is_featured', 'is_active', 'yarn_type')
    search_fields = ('title', 'description', 'sku')
    prepopulated_fields = {'slug': ('title',)}
    fieldsets = (
        ('Basic Info', {'fields': ('category', 'title', 'slug', 'description', 'short_description')}),
        ('SEO', {'fields': ('meta_title', 'meta_description'), 'classes': ('collapse',)}),
        ('Pricing & Stock', {'fields': ('price', 'compare_at_price', 'cost_price', 'stock', 'sku', 'weight')}),
        ('Images', {'fields': ('image', 'image_alt', 'image_3', 'image_4')}),
        ('Attributes', {'fields': ('yarn_type', 'available_sizes', 'available_colors', 'care_instructions'), 'classes': ('collapse',)}),
        ('Visibility', {'fields': ('is_featured', 'is_active')}),
    )

    def avg_rating_display(self, obj):
        r = obj.avg_rating
        return f'{r}★' if r else '—'
    avg_rating_display.short_description = 'Rating'


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    readonly_fields = ('product', 'product_title', 'price', 'quantity', 'size', 'color', 'line_total_display')
    extra = 0
    can_delete = False

    def line_total_display(self, obj):
        return f'PKR {obj.line_total:,.2f}'
    line_total_display.short_description = 'Line Total'


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('short_id', 'full_name', 'phone', 'city', 'total_display', 'payment_method', 'payment_status', 'status', 'created_at')
    list_filter = ('status', 'payment_method', 'payment_status', 'city', 'province', 'created_at')
    search_fields = ('full_name', 'phone', 'email', 'order_id', 'payment_transaction_id')
    readonly_fields = ('order_id', 'created_at', 'updated_at', 'subtotal', 'discount_amount', 'shipping_cost', 'paid_at')
    list_editable = ('status',)
    inlines = [OrderItemInline]
    fieldsets = (
        ('Order Info', {'fields': ('order_id', 'status', 'subtotal', 'discount_amount', 'shipping_cost', 'total', 'coupon', 'note')}),
        ('Payment', {'fields': ('payment_method', 'payment_status', 'payment_transaction_id', 'paid_at')}),
        ('Customer', {'fields': ('user', 'full_name', 'email', 'phone')}),
        ('Shipping Address', {'fields': ('address_line_1', 'address_line_2', 'city', 'province', 'postal_code')}),
        ('Tracking', {'fields': ('tracking_number', 'tracking_url', 'shipped_at', 'delivered_at')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )

    def total_display(self, obj):
        return f'PKR {obj.total:,.2f}'
    total_display.short_description = 'Total'

    def discount_display(self, obj):
        if obj.discount_amount > 0:
            return f'-PKR {obj.discount_amount:,.0f}'
        return '—'
    discount_display.short_description = 'Discount'


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'name', 'rating', 'is_approved', 'is_verified_purchase', 'created_at')
    list_filter = ('is_approved', 'rating', 'created_at')
    list_editable = ('is_approved',)
    search_fields = ('name', 'email', 'comment', 'product__title')
    actions = ['approve_reviews', 'reject_reviews']

    def approve_reviews(self, request, queryset):
        queryset.update(is_approved=True)
        self.message_user(request, f'{queryset.count()} reviews approved.')
    approve_reviews.short_description = 'Approve selected reviews'

    def reject_reviews(self, request, queryset):
        queryset.update(is_approved=False)
        self.message_user(request, f'{queryset.count()} reviews rejected.')
    reject_reviews.short_description = 'Reject selected reviews'


@admin.register(WishlistItem)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'added_at')
    list_filter = ('added_at',)
    search_fields = ('user__username', 'product__title')


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount_type', 'discount_value', 'minimum_order', 'times_used', 'max_uses', 'is_valid_display', 'is_active')
    list_filter = ('discount_type', 'is_active')
    list_editable = ('is_active',)
    search_fields = ('code', 'description')

    def is_valid_display(self, obj):
        return '✅' if obj.is_valid else '❌'
    is_valid_display.short_description = 'Valid?'


@admin.register(NewsletterSubscriber)
class NewsletterAdmin(admin.ModelAdmin):
    list_display = ('email', 'name', 'is_active', 'subscribed_at')
    list_filter = ('is_active', 'subscribed_at')
    search_fields = ('email', 'name')
    actions = ['export_emails']

    def export_emails(self, request, queryset):
        emails = ', '.join(queryset.values_list('email', flat=True))
        self.message_user(request, f'Emails: {emails}')
    export_emails.short_description = 'Copy email addresses'


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'is_read', 'is_resolved', 'created_at')
    list_filter = ('subject', 'is_read', 'is_resolved', 'created_at')
    list_editable = ('is_read', 'is_resolved')
    search_fields = ('name', 'email', 'message')
    readonly_fields = ('name', 'email', 'phone', 'subject', 'message', 'order_id', 'created_at')


@admin.register(ShippingRate)
class ShippingRateAdmin(admin.ModelAdmin):
    list_display = ('city', 'rate', 'free_above', 'estimated_days', 'is_active')
    list_editable = ('rate', 'free_above', 'estimated_days', 'is_active')
    search_fields = ('city',)
