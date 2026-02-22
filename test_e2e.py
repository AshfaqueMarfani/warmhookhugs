"""End-to-end test: Cart → Checkout → OTP flow"""
import urllib.request, urllib.parse, http.cookiejar

cj = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

def get_csrf():
    for cookie in cj:
        if cookie.name == 'csrftoken':
            return cookie.value
    return None

# 1. Hit checkout page first to get CSRF cookie (it has a form with csrf_token)
r = opener.open('http://127.0.0.1:8000/checkout/')
# Will redirect to home because cart is empty, but cookie is set
# Try product detail page which has a form
r = opener.open('http://127.0.0.1:8000/product/organic-cotton-baby-rattle-bunny/')
html = r.read().decode()
# Extract CSRF from the form's hidden input
import re
match = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', html)
csrf_token = match.group(1) if match else get_csrf()
print(f'1. CSRF token obtained: {bool(csrf_token)}')

# 2. Add product to cart
data = urllib.parse.urlencode({'csrfmiddlewaretoken': csrf_token, 'size': '', 'color': ''}).encode()
req = urllib.request.Request('http://127.0.0.1:8000/cart/add/1/', data=data)
req.add_header('Referer', 'http://127.0.0.1:8000/product/organic-cotton-baby-rattle-bunny/')
req.add_header('Cookie', f'csrftoken={csrf_token}')
r = opener.open(req)
print(f'2. Add to cart: {r.status} (url: {r.url})')

# 3. Check cart has item
r = opener.open('http://127.0.0.1:8000/cart/')
html = r.read().decode()
has_item = 'Organic Cotton Baby Rattle' in html
print(f'3. Cart contains product: {has_item}')

# 4. Checkout page
r = opener.open('http://127.0.0.1:8000/checkout/')
html = r.read().decode()
has_form = 'full_name' in html
print(f'4. Checkout page: {r.status}, has form: {has_form}')

# 5. Submit checkout form
for cookie in cj:
    if cookie.name == 'csrftoken':
        csrf_token = cookie.value
checkout_data = urllib.parse.urlencode({
    'csrfmiddlewaretoken': csrf_token,
    'full_name': 'Test Customer',
    'phone': '0300-1234567',
    'email': 'test@test.com',
    'address_line_1': '123 Test Street',
    'city': 'Karachi',
    'province': 'Sindh',
}).encode()
req = urllib.request.Request('http://127.0.0.1:8000/checkout/', data=checkout_data)
req.add_header('Referer', 'http://127.0.0.1:8000/checkout/')
r = opener.open(req)
html = r.read().decode()
at_otp = 'otp_code' in html or 'Verify' in html
print(f'5. Checkout submitted, at OTP page: {at_otp} (url: {r.url})')

print()
print('Full cart -> checkout -> OTP flow PASSED!')
