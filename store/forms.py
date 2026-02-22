"""
Warm Hook Hugs — Forms
========================
Checkout, OTP, Contact, Review, Newsletter, Coupon, Search, Auth.
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User

# Tailwind input classes
INPUT_CLASS = 'w-full px-4 py-3 border border-stone-300 rounded-lg focus:ring-2 focus:ring-amber-600 focus:border-transparent bg-white text-charcoal'
SELECT_CLASS = INPUT_CLASS
TEXTAREA_CLASS = INPUT_CLASS


class CheckoutForm(forms.Form):
    full_name = forms.CharField(max_length=200, widget=forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Full Name'}))
    email = forms.EmailField(required=False, widget=forms.EmailInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Email (optional)'}))
    phone = forms.CharField(max_length=20, help_text='Pakistani mobile number (e.g., 03XX-XXXXXXX)', widget=forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': '03XX-XXXXXXX'}))
    address_line_1 = forms.CharField(max_length=300, widget=forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Street Address'}))
    address_line_2 = forms.CharField(max_length=300, required=False, widget=forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Apartment, suite, etc. (optional)'}))
    city = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'City'}))
    province = forms.ChoiceField(
        required=False,
        choices=[
            ('', 'Select Province'),
            ('Punjab', 'Punjab'),
            ('Sindh', 'Sindh'),
            ('KPK', 'Khyber Pakhtunkhwa'),
            ('Balochistan', 'Balochistan'),
            ('Islamabad', 'Islamabad Capital Territory'),
            ('AJK', 'Azad Jammu & Kashmir'),
            ('GB', 'Gilgit-Baltistan'),
        ],
        widget=forms.Select(attrs={'class': SELECT_CLASS})
    )
    postal_code = forms.CharField(max_length=10, required=False, widget=forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Postal Code (optional)'}))
    note = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': TEXTAREA_CLASS, 'placeholder': 'Special instructions for your order...', 'rows': 3}))
    coupon_code = forms.CharField(max_length=30, required=False, widget=forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Discount Code'}))
    payment_method = forms.ChoiceField(
        choices=[
            ('cod', 'Cash on Delivery'),
            ('card', 'Credit / Debit Card'),
            ('easypaisa', 'EasyPaisa'),
            ('jazzcash', 'JazzCash'),
        ],
        initial='cod',
        widget=forms.RadioSelect(attrs={'class': 'payment-method-radio'}),
    )


class OTPForm(forms.Form):
    otp_code = forms.CharField(
        max_length=6, min_length=6,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-6 py-4 text-center text-3xl tracking-[0.5em] font-mono border-2 border-stone-300 rounded-xl focus:ring-2 focus:ring-amber-600 focus:border-transparent bg-white',
            'placeholder': '● ● ● ● ● ●',
            'maxlength': '6', 'autocomplete': 'one-time-code',
            'inputmode': 'numeric', 'pattern': '[0-9]{6}',
        })
    )


class ContactForm(forms.Form):
    SUBJECT_CHOICES = [
        ('general', 'General Inquiry'),
        ('order', 'Order Support'),
        ('custom', 'Custom Order Request'),
        ('wholesale', 'Wholesale / B2B'),
        ('feedback', 'Feedback'),
        ('other', 'Other'),
    ]
    name = forms.CharField(max_length=200, widget=forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Your Name'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': INPUT_CLASS, 'placeholder': 'your@email.com'}))
    phone = forms.CharField(max_length=20, required=False, widget=forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Phone Number (optional)'}))
    subject = forms.ChoiceField(choices=SUBJECT_CHOICES, widget=forms.Select(attrs={'class': SELECT_CLASS}))
    order_id = forms.CharField(max_length=50, required=False, widget=forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Order ID (if applicable)'}))
    message = forms.CharField(widget=forms.Textarea(attrs={'class': TEXTAREA_CLASS, 'placeholder': 'How can we help you?', 'rows': 5}))


class ReviewForm(forms.Form):
    name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Your Name'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': INPUT_CLASS, 'placeholder': 'your@email.com'}))
    rating = forms.IntegerField(min_value=1, max_value=5, widget=forms.HiddenInput(attrs={'id': 'rating-input'}))
    title = forms.CharField(max_length=200, required=False, widget=forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Review Title (optional)'}))
    comment = forms.CharField(widget=forms.Textarea(attrs={'class': TEXTAREA_CLASS, 'placeholder': 'Share your experience with this product...', 'rows': 4}))


class NewsletterForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'flex-1 px-4 py-3 border border-stone-300 rounded-l-lg focus:ring-2 focus:ring-amber-600 focus:border-transparent bg-white',
        'placeholder': 'Enter your email'
    }))
    name = forms.CharField(max_length=100, required=False, widget=forms.HiddenInput())


class CouponApplyForm(forms.Form):
    coupon_code = forms.CharField(max_length=30, widget=forms.TextInput(attrs={
        'class': 'flex-1 px-4 py-3 border border-stone-300 rounded-l-lg focus:ring-2 focus:ring-amber-600 focus:border-transparent bg-white uppercase',
        'placeholder': 'Enter discount code'
    }))


class SearchForm(forms.Form):
    q = forms.CharField(max_length=200, required=False, widget=forms.TextInput(attrs={
        'class': 'w-full px-4 py-3 pl-10 border border-stone-300 rounded-lg focus:ring-2 focus:ring-amber-600 focus:border-transparent bg-white',
        'placeholder': 'Search products...',
        'autocomplete': 'off',
    }))


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Email'}))
    first_name = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'First Name'}))
    last_name = forms.CharField(max_length=50, required=False, widget=forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Last Name'}))

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'username', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Username'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'class': INPUT_CLASS, 'placeholder': 'Password'})
        self.fields['password2'].widget.attrs.update({'class': INPUT_CLASS, 'placeholder': 'Confirm Password'})


class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Username or Email'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Password'}))


class ProfileForm(forms.Form):
    first_name = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'class': INPUT_CLASS}))
    last_name = forms.CharField(max_length=50, required=False, widget=forms.TextInput(attrs={'class': INPUT_CLASS}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': INPUT_CLASS}))
    phone = forms.CharField(max_length=20, required=False, widget=forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': '03XX-XXXXXXX'}))
