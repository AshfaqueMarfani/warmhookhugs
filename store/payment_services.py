"""
Warm Hook Hugs — Payment Gateway Services
=============================================
Stubs for Card (Stripe/HBL), EasyPaisa, and JazzCash integrations.
Replace the TODO sections with real API calls when you have credentials.

Each gateway follows the same pattern:
  1. initiate_payment(order) → returns redirect URL or client token
  2. verify_payment(request)  → returns (success: bool, transaction_id: str, error: str)
  3. process_refund(order)    → returns (success: bool, error: str)
"""

import hashlib
import hmac
import json
import logging
from datetime import datetime
from decimal import Decimal

from django.conf import settings
from django.urls import reverse

logger = logging.getLogger(__name__)


# ══════════════════════════════════════════════
# PAYMENT METHOD REGISTRY
# ══════════════════════════════════════════════
PAYMENT_METHODS = {
    'cod': {
        'name': 'Cash on Delivery',
        'icon': '💰',
        'description': 'Pay when your order is delivered.',
        'online': False,
    },
    'card': {
        'name': 'Credit / Debit Card',
        'icon': '💳',
        'description': 'Visa, Mastercard, UnionPay.',
        'online': True,
    },
    'easypaisa': {
        'name': 'EasyPaisa',
        'icon': '📱',
        'description': 'Pay via EasyPaisa mobile wallet.',
        'online': True,
    },
    'jazzcash': {
        'name': 'JazzCash',
        'icon': '📱',
        'description': 'Pay via JazzCash mobile wallet.',
        'online': True,
    },
}


def get_payment_methods():
    """Return list of available payment methods for templates."""
    return [
        {'key': k, **v}
        for k, v in PAYMENT_METHODS.items()
    ]


def is_online_payment(method):
    """Check if a payment method requires online processing."""
    return PAYMENT_METHODS.get(method, {}).get('online', False)


# ══════════════════════════════════════════════
# CARD PAYMENTS (Stripe / HBL / PayMob)
# ══════════════════════════════════════════════
class CardPaymentService:
    """
    Card payment gateway integration.
    Default: Stripe. Switch via PAYMENT_CARD_PROVIDER setting.

    TODO: Replace with real Stripe/HBL/PayMob API calls.
    """

    @staticmethod
    def initiate_payment(order, request):
        """
        Create a payment session and return the redirect URL or client secret.

        For Stripe Checkout:
          - Create a Stripe Checkout Session
          - Return session.url for redirect

        For Stripe Elements (embedded):
          - Create a PaymentIntent
          - Return client_secret for frontend JS

        Returns:
            dict: {
                'success': bool,
                'redirect_url': str or None,
                'client_secret': str or None,  # for embedded card form
                'session_id': str or None,
                'error': str or None,
            }
        """
        provider = getattr(settings, 'PAYMENT_CARD_PROVIDER', 'stripe')

        logger.info(
            f"[Card Payment] Initiating {provider} payment for order "
            f"{order.short_id} — PKR {order.total}"
        )

        # ── STRIPE IMPLEMENTATION (uncomment when ready) ──
        #
        # import stripe
        # stripe.api_key = settings.STRIPE_SECRET_KEY
        #
        # try:
        #     checkout_session = stripe.checkout.Session.create(
        #         payment_method_types=['card'],
        #         line_items=[{
        #             'price_data': {
        #                 'currency': 'pkr',
        #                 'product_data': {
        #                     'name': f'Order {order.short_id} — Warm Hook Hugs',
        #                 },
        #                 'unit_amount': int(order.total * 100),  # Stripe uses paisa
        #             },
        #             'quantity': 1,
        #         }],
        #         mode='payment',
        #         success_url=request.build_absolute_uri(
        #             reverse('store:payment_success') + f'?order_id={order.order_id}'
        #         ),
        #         cancel_url=request.build_absolute_uri(
        #             reverse('store:payment_cancel') + f'?order_id={order.order_id}'
        #         ),
        #         metadata={
        #             'order_id': str(order.order_id),
        #             'short_id': order.short_id,
        #         },
        #     )
        #     return {
        #         'success': True,
        #         'redirect_url': checkout_session.url,
        #         'session_id': checkout_session.id,
        #         'error': None,
        #     }
        # except stripe.error.StripeError as e:
        #     logger.error(f"[Stripe] Error: {e}")
        #     return {
        #         'success': False,
        #         'redirect_url': None,
        #         'session_id': None,
        #         'error': str(e),
        #     }

        # ── SIMULATION (dev mode) ──
        success_url = request.build_absolute_uri(
            reverse('store:payment_success') + f'?order_id={order.order_id}'
        )
        logger.info(f"[Card Payment] SIMULATED — Redirecting to success URL")
        return {
            'success': True,
            'redirect_url': success_url,
            'client_secret': None,
            'session_id': f'sim_card_{order.short_id}',
            'error': None,
        }

    @staticmethod
    def verify_payment(request):
        """
        Verify payment after redirect back from gateway.

        Returns:
            dict: {
                'success': bool,
                'transaction_id': str,
                'error': str or None,
            }
        """
        order_id = request.GET.get('order_id', '')

        # ── STRIPE VERIFICATION (uncomment when ready) ──
        #
        # import stripe
        # stripe.api_key = settings.STRIPE_SECRET_KEY
        # session_id = request.GET.get('session_id', '')
        # try:
        #     session = stripe.checkout.Session.retrieve(session_id)
        #     if session.payment_status == 'paid':
        #         return {
        #             'success': True,
        #             'transaction_id': session.payment_intent,
        #             'error': None,
        #         }
        #     return {
        #         'success': False,
        #         'transaction_id': '',
        #         'error': 'Payment not completed.',
        #     }
        # except stripe.error.StripeError as e:
        #     return {
        #         'success': False,
        #         'transaction_id': '',
        #         'error': str(e),
        #     }

        # ── SIMULATION ──
        return {
            'success': True,
            'transaction_id': f'sim_txn_card_{datetime.now().strftime("%Y%m%d%H%M%S")}',
            'error': None,
        }

    @staticmethod
    def process_refund(order):
        """
        Process a refund for a paid card order.

        Returns:
            dict: {'success': bool, 'refund_id': str, 'error': str or None}
        """
        logger.info(f"[Card Refund] Processing refund for {order.short_id}")

        # ── STRIPE REFUND (uncomment when ready) ──
        # import stripe
        # stripe.api_key = settings.STRIPE_SECRET_KEY
        # try:
        #     refund = stripe.Refund.create(
        #         payment_intent=order.payment_transaction_id,
        #     )
        #     return {'success': True, 'refund_id': refund.id, 'error': None}
        # except stripe.error.StripeError as e:
        #     return {'success': False, 'refund_id': '', 'error': str(e)}

        return {
            'success': True,
            'refund_id': f'sim_refund_{order.short_id}',
            'error': None,
        }


# ══════════════════════════════════════════════
# EASYPAISA
# ══════════════════════════════════════════════
class EasyPaisaService:
    """
    EasyPaisa Payment Gateway Integration.

    Docs: https://easypay.easypaisa.com.pk/
    Environments:
      - Sandbox: https://easypaystg.easypaisa.com.pk/
      - Production: https://easypay.easypaisa.com.pk/

    TODO: Replace simulation with real API calls when credentials are ready.
    """

    BASE_URLS = {
        'sandbox': 'https://easypaystg.easypaisa.com.pk/easypay/Index.jsf',
        'production': 'https://easypay.easypaisa.com.pk/easypay/Index.jsf',
    }

    @classmethod
    def _get_base_url(cls):
        env = getattr(settings, 'EASYPAISA_ENVIRONMENT', 'sandbox')
        return cls.BASE_URLS.get(env, cls.BASE_URLS['sandbox'])

    @staticmethod
    def _generate_hash(params_str):
        """Generate HMAC hash for EasyPaisa request validation."""
        hash_key = getattr(settings, 'EASYPAISA_HASH_KEY', 'DUMMY_HASH_KEY')
        return hashlib.sha256(
            (hash_key + params_str).encode('utf-8')
        ).hexdigest()

    @classmethod
    def initiate_payment(cls, order, request):
        """
        Initiate EasyPaisa hosted checkout.

        Returns:
            dict: {'success': bool, 'redirect_url': str, 'error': str or None}
        """
        store_id = getattr(settings, 'EASYPAISA_STORE_ID', 'DUMMY_STORE_ID')

        logger.info(
            f"[EasyPaisa] Initiating payment for {order.short_id} — PKR {order.total}"
        )

        # ── REAL IMPLEMENTATION (uncomment when ready) ──
        #
        # amount = str(order.total)
        # order_ref = str(order.order_id)
        # postback_url = request.build_absolute_uri(reverse('store:payment_callback_easypaisa'))
        #
        # params = {
        #     'storeId': store_id,
        #     'amount': amount,
        #     'postBackURL': postback_url,
        #     'orderRefNum': order_ref,
        #     'expiryDate': (timezone.now() + timedelta(hours=1)).strftime('%Y%m%d %H%M%S'),
        #     'autoRedirect': '1',
        #     'paymentMethod': 'InitialRequest',
        #     'emailAddr': order.email or '',
        #     'mobileNum': order.phone,
        # }
        #
        # # Generate hash
        # hash_string = '&'.join(f'{k}={v}' for k, v in sorted(params.items()))
        # params['merchantHashedReq'] = cls._generate_hash(hash_string)
        #
        # # Build redirect URL with params
        # base_url = cls._get_base_url()
        # query_string = '&'.join(f'{k}={v}' for k, v in params.items())
        # redirect_url = f'{base_url}?{query_string}'
        #
        # return {'success': True, 'redirect_url': redirect_url, 'error': None}

        # ── SIMULATION ──
        success_url = request.build_absolute_uri(
            reverse('store:payment_success') + f'?order_id={order.order_id}'
        )
        return {'success': True, 'redirect_url': success_url, 'error': None}

    @staticmethod
    def verify_payment(request):
        """
        Verify EasyPaisa payment via postback/callback.

        Returns:
            dict: {'success': bool, 'transaction_id': str, 'error': str or None}
        """
        # ── REAL IMPLEMENTATION (uncomment when ready) ──
        #
        # response_code = request.POST.get('responseCode') or request.GET.get('responseCode')
        # transaction_id = request.POST.get('transactionId') or request.GET.get('transactionId')
        #
        # if response_code == '0000':
        #     return {'success': True, 'transaction_id': transaction_id, 'error': None}
        # return {
        #     'success': False,
        #     'transaction_id': transaction_id or '',
        #     'error': f'EasyPaisa response code: {response_code}',
        # }

        # ── SIMULATION ──
        return {
            'success': True,
            'transaction_id': f'sim_txn_ep_{datetime.now().strftime("%Y%m%d%H%M%S")}',
            'error': None,
        }


# ══════════════════════════════════════════════
# JAZZCASH
# ══════════════════════════════════════════════
class JazzCashService:
    """
    JazzCash Payment Gateway Integration.

    Docs: https://sandbox.jazzcash.com.pk/SandboxDocumentation
    Environments:
      - Sandbox: https://sandbox.jazzcash.com.pk/
      - Production: https://payments.jazzcash.com.pk/

    TODO: Replace simulation with real API calls when credentials are ready.
    """

    BASE_URLS = {
        'sandbox': 'https://sandbox.jazzcash.com.pk/CustomerPortal/transactionmanagement/merchantform/',
        'production': 'https://payments.jazzcash.com.pk/CustomerPortal/transactionmanagement/merchantform/',
    }

    @classmethod
    def _get_base_url(cls):
        env = getattr(settings, 'JAZZCASH_ENVIRONMENT', 'sandbox')
        return cls.BASE_URLS.get(env, cls.BASE_URLS['sandbox'])

    @staticmethod
    def _generate_hash(params):
        """Generate HMAC-SHA256 hash for JazzCash request."""
        integrity_salt = getattr(settings, 'JAZZCASH_INTEGRITY_SALT', 'DUMMY_SALT')
        sorted_values = '&'.join(str(v) for k, v in sorted(params.items()) if v)
        hash_string = integrity_salt + '&' + sorted_values
        return hmac.new(
            integrity_salt.encode('utf-8'),
            hash_string.encode('utf-8'),
            hashlib.sha256,
        ).hexdigest()

    @classmethod
    def initiate_payment(cls, order, request):
        """
        Initiate JazzCash hosted checkout.

        Returns:
            dict: {'success': bool, 'redirect_url': str, 'form_data': dict, 'error': str or None}
        """
        merchant_id = getattr(settings, 'JAZZCASH_MERCHANT_ID', 'DUMMY_MERCHANT_ID')
        password = getattr(settings, 'JAZZCASH_PASSWORD', 'DUMMY_PASSWORD')

        logger.info(
            f"[JazzCash] Initiating payment for {order.short_id} — PKR {order.total}"
        )

        # ── REAL IMPLEMENTATION (uncomment when ready) ──
        #
        # from datetime import timedelta
        # now = timezone.now()
        # txn_datetime = now.strftime('%Y%m%d%H%M%S')
        # expiry = (now + timedelta(hours=1)).strftime('%Y%m%d%H%M%S')
        #
        # params = {
        #     'pp_Version': '1.1',
        #     'pp_TxnType': 'MWALLET',
        #     'pp_Language': 'EN',
        #     'pp_MerchantID': merchant_id,
        #     'pp_Password': password,
        #     'pp_TxnRefNo': f'T{txn_datetime}',
        #     'pp_Amount': str(int(order.total * 100)),  # In paisa
        #     'pp_TxnCurrency': 'PKR',
        #     'pp_TxnDateTime': txn_datetime,
        #     'pp_TxnExpiryDateTime': expiry,
        #     'pp_BillReference': str(order.order_id)[:20],
        #     'pp_Description': f'Order {order.short_id}',
        #     'pp_ReturnURL': request.build_absolute_uri(reverse('store:payment_callback_jazzcash')),
        #     'pp_MobileNumber': order.phone,
        # }
        # params['pp_SecureHash'] = cls._generate_hash(params)
        #
        # return {
        #     'success': True,
        #     'redirect_url': cls._get_base_url(),
        #     'form_data': params,
        #     'error': None,
        # }

        # ── SIMULATION ──
        success_url = request.build_absolute_uri(
            reverse('store:payment_success') + f'?order_id={order.order_id}'
        )
        return {'success': True, 'redirect_url': success_url, 'form_data': {}, 'error': None}

    @staticmethod
    def verify_payment(request):
        """
        Verify JazzCash payment via callback.

        Returns:
            dict: {'success': bool, 'transaction_id': str, 'error': str or None}
        """
        # ── REAL IMPLEMENTATION (uncomment when ready) ──
        #
        # response_code = request.POST.get('pp_ResponseCode', '')
        # txn_ref = request.POST.get('pp_TxnRefNo', '')
        # retrieval_ref = request.POST.get('pp_RetrievalReferenceNo', '')
        #
        # if response_code == '000':
        #     return {'success': True, 'transaction_id': retrieval_ref or txn_ref, 'error': None}
        # msg = request.POST.get('pp_ResponseMessage', 'Payment failed')
        # return {'success': False, 'transaction_id': txn_ref, 'error': msg}

        # ── SIMULATION ──
        return {
            'success': True,
            'transaction_id': f'sim_txn_jc_{datetime.now().strftime("%Y%m%d%H%M%S")}',
            'error': None,
        }


# ══════════════════════════════════════════════
# UNIFIED PAYMENT DISPATCHER
# ══════════════════════════════════════════════
def initiate_payment(order, request):
    """
    Route payment to the correct gateway based on order.payment_method.

    Returns:
        dict with 'success', 'redirect_url', 'error' keys.
    """
    method = order.payment_method

    if method == 'cod':
        # No payment processing needed for COD
        return {'success': True, 'redirect_url': None, 'error': None}

    elif method == 'card':
        return CardPaymentService.initiate_payment(order, request)

    elif method == 'easypaisa':
        return EasyPaisaService.initiate_payment(order, request)

    elif method == 'jazzcash':
        return JazzCashService.initiate_payment(order, request)

    else:
        return {'success': False, 'redirect_url': None, 'error': f'Unknown payment method: {method}'}


def verify_payment(method, request):
    """
    Verify payment callback from any gateway.

    Returns:
        dict with 'success', 'transaction_id', 'error' keys.
    """
    if method == 'card':
        return CardPaymentService.verify_payment(request)
    elif method == 'easypaisa':
        return EasyPaisaService.verify_payment(request)
    elif method == 'jazzcash':
        return JazzCashService.verify_payment(request)
    else:
        return {'success': False, 'transaction_id': '', 'error': f'Unknown method: {method}'}
