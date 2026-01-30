from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..schemas import UsageResponse, PaymentResponse, SubscriptionResponse
from ..services.billing_service import BillingService
from ..utils.deps import get_current_user
from ..models import APIKey, Payment, Subscription, Invoice

router = APIRouter()

@router.get("/usage", response_model=UsageResponse)
def get_usage(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    api_key = db.query(APIKey).filter(APIKey.owner_id == current_user.id).first()
    if not api_key:
        return {"daily_usage": 0, "monthly_usage": 0, "plan": "none", "status": "none"}
    plan_name = api_key.plan.name if api_key.plan else "none"
    return {
        "daily_usage": api_key.daily_usage,
        "monthly_usage": api_key.monthly_usage,
        "plan": plan_name,
        "status": api_key.status
    }

@router.get("/payments", response_model=list[PaymentResponse])
def get_payments(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    payments = db.query(Payment).filter(Payment.user_id == current_user.id).all()
    return payments

@router.get("/subscription", response_model=SubscriptionResponse)
def get_subscription(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    subscription = db.query(Subscription).filter(Subscription.user_id == current_user.id, Subscription.status == 'active').first()
    if not subscription:
        raise HTTPException(status_code=404, detail="No active subscription")
    return subscription

@router.get("/billing-summary")
def get_billing_summary(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    """Get billing summary for dashboard"""
    # Total paid
    total_paid = db.query(Payment).filter(
        Payment.user_id == current_user.id,
        Payment.status == 'succeeded'
    ).with_entities(db.func.sum(Payment.amount)).scalar() or 0

    # Pending invoices
    pending_invoices = db.query(Invoice).filter(
        Invoice.user_id == current_user.id,
        Invoice.status.in_(['open', 'failed'])
    ).count()

    # Last payment
    last_payment = db.query(Payment).filter(
        Payment.user_id == current_user.id,
        Payment.status == 'succeeded'
    ).order_by(Payment.created_at.desc()).first()

    return {
        "total_paid": total_paid,
        "pending_invoices": pending_invoices,
        "last_payment_date": last_payment.created_at if last_payment else None,
        "currency": "usd"
    }