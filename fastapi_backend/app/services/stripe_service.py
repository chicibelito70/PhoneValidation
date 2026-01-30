import stripe
import os
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from ..models import Payment, APIKey, User, Subscription, Plan
from ..services.billing_service import BillingService
from datetime import datetime

load_dotenv()

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

def create_or_get_customer(user: User):
    if user.stripe_customer_id:
        return stripe.Customer.retrieve(user.stripe_customer_id)
    customer = stripe.Customer.create(email=user.email)
    user.stripe_customer_id = customer.id
    return customer

def create_checkout_session(db: Session, user: User, plan: Plan):
    customer = create_or_get_customer(user)
    session = stripe.checkout.Session.create(
        customer=customer.id,
        payment_method_types=['card'],
        line_items=[{
            'price': plan.stripe_price_id,
            'quantity': 1,
        }],
        mode='subscription',
        success_url='http://localhost:3000/success',
        cancel_url='http://localhost:3000/cancel',
        metadata={'user_id': str(user.id), 'plan_id': str(plan.id)}
    )
    return session

def handle_webhook(db: Session, payload: str, sig_header: str):
    endpoint_secret = os.getenv("STRIPE_WEBHOOK_SECRET")
    event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)

    event_type = event['type']
    data = event['data']['object']

    if event_type == 'checkout.session.completed':
        handle_checkout_completed(db, data)
    elif event_type == 'customer.subscription.created':
        handle_subscription_created(db, data)
    elif event_type == 'customer.subscription.updated':
        handle_subscription_updated(db, data)
    elif event_type == 'customer.subscription.deleted':
        handle_subscription_deleted(db, data)
    elif event_type == 'invoice.created':
        handle_invoice_created(db, data)
    elif event_type == 'invoice.finalized':
        handle_invoice_finalized(db, data)
    elif event_type == 'invoice.payment_succeeded':
        handle_invoice_payment_succeeded(db, data)
    elif event_type == 'invoice.payment_failed':
        handle_invoice_payment_failed(db, data)
    elif event_type == 'invoice.voided':
        handle_invoice_voided(db, data)

    return event

def handle_checkout_completed(db: Session, session):
    user_id = int(session['metadata']['user_id'])
    plan_id = int(session['metadata']['plan_id'])
    # Subscription will be created via webhook

def handle_subscription_created(db: Session, subscription):
    user_id = int(subscription['metadata'].get('user_id'))
    plan_id = int(subscription['metadata'].get('plan_id'))
    db_subscription = Subscription(
        user_id=user_id,
        stripe_subscription_id=subscription['id'],
        plan_id=plan_id,
        status=subscription['status'],
        current_period_start=datetime.fromtimestamp(subscription['current_period_start']),
        current_period_end=datetime.fromtimestamp(subscription['current_period_end'])
    )
    db.add(db_subscription)
    db.commit()
    # Activate API keys
    activate_user_api_keys(db, user_id)

def handle_subscription_updated(db: Session, subscription):
    db_sub = db.query(Subscription).filter(Subscription.stripe_subscription_id == subscription['id']).first()
    if db_sub:
        db_sub.status = subscription['status']
        db_sub.current_period_start = datetime.fromtimestamp(subscription['current_period_start'])
        db_sub.current_period_end = datetime.fromtimestamp(subscription['current_period_end'])
        db_sub.cancel_at_period_end = subscription['cancel_at_period_end']
        db.commit()
        # Update API keys status based on subscription status
        update_api_keys_status(db, db_sub.user_id, subscription['status'])

def handle_subscription_deleted(db: Session, subscription):
    db_sub = db.query(Subscription).filter(Subscription.stripe_subscription_id == subscription['id']).first()
    if db_sub:
        db_sub.status = 'canceled'
        db.commit()
        # Downgrade to free
        downgrade_to_free(db, db_sub.user_id)

def handle_payment_succeeded(db: Session, invoice):
    # Save payment record
    payment = Payment(
        user_id=int(invoice['customer']),
        stripe_invoice_id=invoice['id'],
        amount=invoice['amount_paid'] / 100,  # Convert from cents
        currency=invoice['currency'],
        status='succeeded',
        description=invoice['description'] or 'Subscription payment'
    )
    db.add(payment)
    db.commit()

def handle_invoice_voided(db: Session, invoice):
    """Handle invoice voided"""
    BillingService.update_invoice_status(invoice['id'], 'void', None, db)

def handle_invoice_created(db: Session, invoice):
    """Handle invoice created - save draft invoice"""
    try:
        BillingService.create_invoice_from_stripe(invoice, db)
    except Exception as e:
        print(f"Error creating invoice: {e}")

def handle_invoice_finalized(db: Session, invoice):
    """Handle invoice finalized - invoice is ready for payment"""
    BillingService.update_invoice_status(invoice['id'], 'open', None, db)

def handle_invoice_payment_succeeded(db: Session, invoice):
    """Handle successful payment"""
    paid_at = datetime.fromtimestamp(invoice['status_transitions']['paid_at']) if invoice.get('status_transitions', {}).get('paid_at') else datetime.utcnow()
    BillingService.update_invoice_status(invoice['id'], 'paid', paid_at, db)

    # Reactivate services if they were suspended
    customer_id = invoice['customer']
    user = db.query(User).filter(User.stripe_customer_id == customer_id).first()
    if user:
        activate_user_api_keys(db, user.id)

def handle_invoice_payment_failed(db: Session, invoice):
    """Handle failed payment"""
    BillingService.update_invoice_status(invoice['id'], 'failed', None, db)

    # Suspend services
    customer_id = invoice['customer']
    user = db.query(User).filter(User.stripe_customer_id == customer_id).first()
    if user:
        suspend_user_api_keys(db, user.id)

def activate_user_api_keys(db: Session, user_id: int):
    db.query(APIKey).filter(APIKey.owner_id == user_id).update({"status": "active"})
    db.commit()

def suspend_user_api_keys(db: Session, user_id: int):
    db.query(APIKey).filter(APIKey.owner_id == user_id).update({"status": "suspended"})
    db.commit()

def update_api_keys_status(db: Session, user_id: int, sub_status: str):
    if sub_status in ['active']:
        status = 'active'
    elif sub_status in ['past_due', 'unpaid']:
        status = 'suspended'
    else:
        status = 'blocked'
    db.query(APIKey).filter(APIKey.owner_id == user_id).update({"status": status})
    db.commit()

def downgrade_to_free(db: Session, user_id: int):
    free_plan = db.query(Plan).filter(Plan.name == 'free').first()
    if free_plan:
        db.query(APIKey).filter(APIKey.owner_id == user_id).update({"plan_id": free_plan.id, "status": "active"})
        db.commit()

def cancel_subscription(db: Session, user: User):
    subscription = db.query(Subscription).filter(Subscription.user_id == user.id, Subscription.status == 'active').first()
    if subscription:
        stripe.Subscription.modify(subscription.stripe_subscription_id, cancel_at_period_end=True)
        subscription.cancel_at_period_end = True
        db.commit()

def reactivate_subscription(db: Session, user: User):
    subscription = db.query(Subscription).filter(Subscription.user_id == user.id).first()
    if subscription:
        stripe.Subscription.modify(subscription.stripe_subscription_id, cancel_at_period_end=False)
        subscription.cancel_at_period_end = False
        db.commit()

def change_plan(db: Session, user: User, new_plan: Plan):
    subscription = db.query(Subscription).filter(Subscription.user_id == user.id, Subscription.status == 'active').first()
    if subscription:
        # Update subscription in Stripe
        stripe.Subscription.modify(
            subscription.stripe_subscription_id,
            items=[{
                'id': subscription.stripe_subscription_id + '_item',  # Assuming single item
                'price': new_plan.stripe_price_id,
            }],
            proration_behavior='create_prorations'
        )
        subscription.plan_id = new_plan.id
        db.commit()
        # Update API keys
        db.query(APIKey).filter(APIKey.owner_id == user.id).update({"plan_id": new_plan.id})
        db.commit()