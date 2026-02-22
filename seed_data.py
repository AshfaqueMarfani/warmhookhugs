"""
Warm Hook Hugs — Seed Data Script
====================================
Run: python manage.py shell < seed_data.py
Or:  python seed_data.py
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from store.models import Category, Product

# ══════════════════════════════════════════════
# CATEGORIES (from PROJECT.MD brand architecture)
# ══════════════════════════════════════════════
categories_data = [
    {
        'name': 'The Hug Collection',
        'description': 'Amigurumi & Toys — Organic cotton baby rattles, bedtime plushies, sensory toys for toddlers, and custom name dolls. Each piece is a warm embrace waiting to happen.',
    },
    {
        'name': 'Warmth & Wear',
        'description': 'Apparel — Chunky knit cardigans, newborn booties & beanies, winter scarves, and hand-embroidered sweaters. Wearable warmth crafted with intention.',
    },
    {
        'name': 'Home & Hearth',
        'description': 'Lifestyle & Decor — Textured throw blankets, boho cushion covers, macrame wall hangings, and hand-hooked coasters. Transform your space into a sanctuary.',
    },
    {
        'name': 'Everyday Elegance',
        'description': 'Accessories — Crochet tote bags, laptop sleeves, coin pouches, and keychains. Artisanal elegance for your daily essentials.',
    },
]

print("Creating categories...")
for cat_data in categories_data:
    cat, created = Category.objects.get_or_create(
        name=cat_data['name'],
        defaults={'description': cat_data['description']}
    )
    status = "✅ Created" if created else "⏭️ Exists"
    print(f"  {status}: {cat.name}")

# ══════════════════════════════════════════════
# SAMPLE PRODUCTS
# ══════════════════════════════════════════════
products_data = [
    # The Hug Collection
    {
        'category': 'The Hug Collection',
        'title': 'Organic Cotton Baby Rattle — Bunny',
        'description': 'Handcrafted from 100% organic cotton yarn, this gentle bunny rattle is the perfect first companion for your little one. Soft, safe, and made with love — every stitch carries the warmth of our artisans\' hearts. Machine washable and free from harsh dyes.',
        'price': 2500,
        'stock': 15,
        'yarn_type': 'Organic Cotton',
        'available_colors': 'Blush Pink, Sage Green, Cream',
        'is_featured': True,
    },
    {
        'category': 'The Hug Collection',
        'title': 'Bedtime Plushie — Sleepy Bear',
        'description': 'Meet Sleepy Bear — a bedtime companion crafted from the softest merino wool blend. At 30cm tall, this amigurumi bear is the perfect size for tiny arms. Each bear takes 8+ hours of careful handwork.',
        'price': 4500,
        'stock': 8,
        'yarn_type': 'Merino Wool Blend',
        'available_colors': 'Warm Brown, Honey, Cream',
        'is_featured': True,
    },
    {
        'category': 'The Hug Collection',
        'title': 'Sensory Stacking Rings',
        'description': 'A beautiful set of 5 crocheted stacking rings in earthy tones. Perfect for developing motor skills and sensory exploration. Each ring features a different texture pattern, handmade with baby-safe organic cotton.',
        'price': 3200,
        'stock': 12,
        'yarn_type': 'Organic Cotton',
        'available_colors': 'Earth Tones Set',
    },
    # Warmth & Wear
    {
        'category': 'Warmth & Wear',
        'title': 'Chunky Knit Cardigan — Heritage',
        'description': 'Our signature Heritage cardigan — a chunky knit masterpiece in premium merino wool. Oversized, cozy, and undeniably elegant. Features hand-carved wooden buttons and a relaxed fit that drapes beautifully over any outfit.',
        'price': 12500,
        'compare_at_price': 15000,
        'stock': 5,
        'yarn_type': 'Premium Merino Wool',
        'available_sizes': 'S, M, L, XL',
        'available_colors': 'Oatmeal, Terracotta, Charcoal',
        'is_featured': True,
    },
    {
        'category': 'Warmth & Wear',
        'title': 'Newborn Booties & Beanie Set',
        'description': 'The sweetest welcome for a newborn — matching booties and beanie handcrafted from the softest organic cotton. Gentle elastic ensures a snug fit without restricting movement. Comes in a premium gift box.',
        'price': 3800,
        'stock': 20,
        'yarn_type': 'Organic Cotton',
        'available_sizes': 'Newborn, 0-3M, 3-6M',
        'available_colors': 'White, Blush Pink, Baby Blue, Sage',
        'is_featured': True,
    },
    {
        'category': 'Warmth & Wear',
        'title': 'Winter Scarf — Herringbone',
        'description': 'A luxuriously long herringbone-pattern scarf in double-knit merino wool. 180cm of pure warmth with fringed edges. The kind of scarf you reach for every cold morning.',
        'price': 5500,
        'stock': 10,
        'yarn_type': 'Merino Wool',
        'available_colors': 'Cream, Dusty Rose, Forest Green',
    },
    # Home & Hearth
    {
        'category': 'Home & Hearth',
        'title': 'Textured Throw Blanket — Cloud',
        'description': 'Sink into the Cloud — our bestselling textured throw blanket. A generous 150×200cm of chunky-knit luxury in a stunning bobble stitch pattern. Each blanket takes our artisans over 40 hours to complete.',
        'price': 18000,
        'compare_at_price': 22000,
        'stock': 3,
        'yarn_type': 'Premium Acrylic Blend',
        'available_colors': 'Ivory, Dove Grey, Blush',
        'is_featured': True,
    },
    {
        'category': 'Home & Hearth',
        'title': 'Boho Cushion Cover Set (2 pcs)',
        'description': 'Transform your living space with these handcrafted boho cushion covers featuring intricate geometric patterns. Set of 2, fits standard 45×45cm inserts. The textured surface adds depth and warmth to any room.',
        'price': 6500,
        'stock': 8,
        'yarn_type': 'Cotton Blend',
        'available_colors': 'Natural & Terracotta, Cream & Sage',
    },
    {
        'category': 'Home & Hearth',
        'title': 'Hand-Hooked Coaster Set (6 pcs)',
        'description': 'Six beautiful hand-hooked coasters in complementary earth tones. Each coaster features a unique pattern — no two are exactly alike. Protects your surfaces in style.',
        'price': 1800,
        'stock': 25,
        'yarn_type': 'Cotton',
        'available_colors': 'Earth Tones Mix',
    },
    # Everyday Elegance
    {
        'category': 'Everyday Elegance',
        'title': 'Crochet Tote Bag — Market Day',
        'description': 'The Market Day tote — a spacious, sturdy crochet bag perfect for groceries, beach days, or everyday errands. Reinforced handles, cotton-lined interior pocket, and a structure that holds its shape beautifully.',
        'price': 4800,
        'stock': 10,
        'yarn_type': 'Jute & Cotton',
        'available_colors': 'Natural, Terracotta Trim, Black Trim',
        'is_featured': True,
    },
    {
        'category': 'Everyday Elegance',
        'title': 'Laptop Sleeve — 13"',
        'description': 'Protect your laptop in artisanal style. This padded crochet sleeve fits 13" laptops snugly with a button-loop closure. Thick enough to cushion, slim enough to slide into any bag.',
        'price': 3500,
        'stock': 7,
        'yarn_type': 'Cotton Blend',
        'available_colors': 'Charcoal, Cream, Terracotta',
    },
    {
        'category': 'Everyday Elegance',
        'title': 'Coin Pouch — Mini Hug',
        'description': 'Our tiniest creation packs the biggest charm. This adorable crocheted coin pouch features a zip closure and fits cards, coins, earbuds, or lipstick. A perfect little gift.',
        'price': 1200,
        'stock': 30,
        'yarn_type': 'Cotton',
        'available_colors': 'Blush, Sage, Lavender, Terracotta, Cream',
        'is_featured': True,
    },
]

print("\nCreating products...")
for p_data in products_data:
    cat_name = p_data.pop('category')
    category = Category.objects.get(name=cat_name)
    product, created = Product.objects.get_or_create(
        title=p_data['title'],
        defaults={**p_data, 'category': category}
    )
    status = "✅ Created" if created else "⏭️ Exists"
    print(f"  {status}: {product.title}")

print("\n🎉 Seed data complete!")
print(f"   Categories: {Category.objects.count()}")
print(f"   Products:   {Product.objects.count()}")
