from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..schemas import CheckoutSessionCreate, CheckoutSessionResponse, ChangePlanRequest, InvoiceResponse, RefundRequest, RefundResponse, UserUpdate
from ..services import create_checkout_session, handle_webhook, cancel_subscription, reactivate_subscription, change_plan
from ..services.billing_service import BillingService
from ..utils.deps import get_current_user
from ..models import Plan, User, Invoice

router = APIRouter()

@router.post("/create-checkout-session", response_model=CheckoutSessionResponse)
def create_checkout(plan_data: CheckoutSessionCreate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    plan = db.query(Plan).filter(Plan.id == plan_data.plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    session = create_checkout_session(db, current_user, plan)
    return {"checkout_url": session.url}

@router.post("/webhook")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    payload = await request.body()
    sig_header = request.headers.get('stripe-signature')
    handle_webhook(db, payload.decode(), sig_header)
    return {"status": "success"}

@router.post("/cancel-subscription")
def cancel_sub(current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    cancel_subscription(db, current_user)
    return {"message": "Subscription canceled"}

@router.post("/reactivate-subscription")
def reactivate_sub(current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    reactivate_subscription(db, current_user)
    return {"message": "Subscription reactivated"}

@router.post("/change-plan")
def change_plan_endpoint(plan_data: ChangePlanRequest, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    new_plan = db.query(Plan).filter(Plan.id == plan_data.new_plan_id).first()
    if not new_plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    change_plan(db, current_user, new_plan)
    return {"message": "Plan changed"}

@router.get("/invoices", response_model=list[InvoiceResponse])
def get_user_invoices(current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get all invoices for the current user"""
    return BillingService.get_user_invoices(current_user.id, db)

@router.get("/invoices/{invoice_id}", response_model=InvoiceResponse)
def get_invoice(invoice_id: int, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get specific invoice details"""
    invoice = BillingService.get_invoice_by_id(invoice_id, current_user.id, db)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return invoice

@router.post("/refund", response_model=RefundResponse)
def create_refund(refund_data: RefundRequest, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    """Create a refund for an invoice"""
    # Verify invoice belongs to user
    invoice = db.query(Invoice).filter(
        Invoice.id == refund_data.invoice_id,
        Invoice.user_id == current_user.id
    ).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")

    try:
        refund = BillingService.process_refund(refund_data.invoice_id, refund_data.amount, db)
        return RefundResponse(**refund)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/tax-info")
def update_tax_info(tax_data: UserUpdate, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    """Update tax information"""
    try:
        BillingService.update_customer_tax_info(current_user.id, tax_data.dict(exclude_unset=True), db)
        return {"message": "Tax information updated"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))