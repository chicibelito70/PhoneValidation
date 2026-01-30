import os
import stripe
from dotenv import load_dotenv
from .api_key_auth import load_api_keys, save_api_keys

load_dotenv()

stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
WEBHOOK_SECRET = os.getenv('STRIPE_WEBHOOK_SECRET')

PRICE_IDS = {
    "free": os.getenv('STRIPE_PRICE_FREE'),
    "pro": os.getenv('STRIPE_PRICE_PRO'),
    "enterprise": os.getenv('STRIPE_PRICE_ENTERPRISE')
}

PLAN_LIMITS = {
    "free": 100,
    "pro": 10000,
    "enterprise": None
}

def create_checkout_session(api_key, plan):
    """
    Crea una sesión de Stripe Checkout para el plan seleccionado.
    """
    if plan not in PRICE_IDS or not PRICE_IDS[plan]:
        raise ValueError("Plan inválido")

    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price': PRICE_IDS[plan],
                'quantity': 1,
            }],
            mode='subscription',  # O 'payment' si es one-time
            success_url='http://localhost:5173/success?session_id={CHECKOUT_SESSION_ID}',
            cancel_url='http://localhost:5173/cancel',
            metadata={
                'api_key': api_key,
                'plan': plan
            }
        )
        return session
    except Exception as e:
        raise Exception(f"Error creando sesión de pago: {str(e)}")

def handle_webhook(payload, sig_header):
    """
    Maneja el webhook de Stripe.
    """
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, WEBHOOK_SECRET
        )
    except ValueError as e:
        raise ValueError("Invalid payload")
    except stripe.error.SignatureVerificationError as e:
        raise ValueError("Invalid signature")

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        api_key = session['metadata']['api_key']
        plan = session['metadata']['plan']
        update_plan_on_payment(api_key, plan)

    return event

def update_plan_on_payment(api_key, plan):
    """
    Actualiza el plan de la API key al completar el pago.
    """
    keys = load_api_keys()
    if api_key in keys:
        keys[api_key]['plan'] = plan
        keys[api_key]['monthly_limit'] = PLAN_LIMITS[plan]
        keys[api_key]['usage_count'] = 0
        keys[api_key]['blocked'] = False
        save_api_keys(keys)