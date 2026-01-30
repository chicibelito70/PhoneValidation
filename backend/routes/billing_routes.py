from flask import Blueprint, request, jsonify
from services.stripe_service import create_checkout_session, handle_webhook
from security.api_key_auth import validate_api_key

billing_bp = Blueprint('billing', __name__)

@billing_bp.route('/api/billing/create-checkout-session', methods=['POST'])
def create_checkout():
    """
    Crea una sesión de checkout para el pago del plan.
    """
    data = request.get_json()
    api_key = data.get('api_key')
    plan = data.get('plan')

    if not api_key or not plan:
        return jsonify({"error": "api_key y plan son requeridos"}), 400

    # Validar que la API key existe
    valid, _ = validate_api_key(api_key)
    if not valid:
        return jsonify({"error": "API Key inválida"}), 403

    try:
        session = create_checkout_session(api_key, plan)
        return jsonify({"checkout_url": session.url})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@billing_bp.route('/api/billing/webhook', methods=['POST'])
def stripe_webhook():
    """
    Webhook para manejar eventos de Stripe.
    """
    payload = request.get_data(as_text=True)
    sig_header = request.headers.get('stripe-signature')

    try:
        event = handle_webhook(payload, sig_header)
        return jsonify({"status": "success"}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400