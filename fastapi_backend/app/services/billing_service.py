from sqlalchemy.orm import Session
from ..models import Invoice, InvoiceItem, User, Subscription
from ..schemas import InvoiceResponse, InvoiceItemResponse
from typing import List, Optional
import stripe
import os
from datetime import datetime

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

class BillingService:
    @staticmethod
    def create_invoice_from_stripe(stripe_invoice: dict, db: Session) -> Invoice:
        """Create or update invoice from Stripe webhook data"""
        invoice_data = {
            "stripe_invoice_id": stripe_invoice["id"],
            "amount": stripe_invoice["amount_due"] / 100,  # Convert from cents
            "currency": stripe_invoice["currency"],
            "status": stripe_invoice["status"],
            "pdf_url": stripe_invoice.get("invoice_pdf"),
            "issued_at": datetime.fromtimestamp(stripe_invoice["created"]),
        }

        if stripe_invoice.get("period_start"):
            invoice_data["period_start"] = datetime.fromtimestamp(stripe_invoice["period_start"])
        if stripe_invoice.get("period_end"):
            invoice_data["period_end"] = datetime.fromtimestamp(stripe_invoice["period_end"])

        # Find user by customer ID
        customer_id = stripe_invoice["customer"]
        user = db.query(User).filter(User.stripe_customer_id == customer_id).first()
        if not user:
            raise ValueError(f"User not found for customer {customer_id}")

        invoice_data["user_id"] = user.id

        # Check if invoice already exists
        existing_invoice = db.query(Invoice).filter(
            Invoice.stripe_invoice_id == stripe_invoice["id"]
        ).first()

        if existing_invoice:
            # Update existing
            for key, value in invoice_data.items():
                setattr(existing_invoice, key, value)
            invoice = existing_invoice
        else:
            # Create new
            invoice = Invoice(**invoice_data)
            db.add(invoice)
            db.flush()  # Get ID

            # Create invoice items
            for item in stripe_invoice.get("lines", {}).get("data", []):
                item_data = {
                    "invoice_id": invoice.id,
                    "description": item["description"],
                    "amount": item["amount"] / 100,
                    "quantity": item["quantity"],
                }
                if item.get("period"):
                    item_data["period_start"] = datetime.fromtimestamp(item["period"]["start"])
                    item_data["period_end"] = datetime.fromtimestamp(item["period"]["end"])

                invoice_item = InvoiceItem(**item_data)
                db.add(invoice_item)

        db.commit()
        return invoice

    @staticmethod
    def update_invoice_status(stripe_invoice_id: str, status: str, paid_at: Optional[datetime], db: Session):
        """Update invoice status"""
        invoice = db.query(Invoice).filter(Invoice.stripe_invoice_id == stripe_invoice_id).first()
        if invoice:
            invoice.status = status
            if paid_at:
                invoice.paid_at = paid_at
            db.commit()

    @staticmethod
    def get_user_invoices(user_id: int, db: Session) -> List[InvoiceResponse]:
        """Get all invoices for a user"""
        invoices = db.query(Invoice).filter(Invoice.user_id == user_id).order_by(Invoice.issued_at.desc()).all()
        return [InvoiceResponse.from_orm(invoice) for invoice in invoices]

    @staticmethod
    def get_invoice_by_id(invoice_id: int, user_id: int, db: Session) -> Optional[InvoiceResponse]:
        """Get specific invoice for user"""
        invoice = db.query(Invoice).filter(
            Invoice.id == invoice_id,
            Invoice.user_id == user_id
        ).first()
        return InvoiceResponse.from_orm(invoice) if invoice else None

    @staticmethod
    def create_usage_invoice_item(user_id: int, description: str, amount: float, db: Session):
        """Create invoice item for additional usage"""
        # This would be called when usage exceeds plan limits
        # For now, just log it - in production, you'd create a draft invoice
        pass

    @staticmethod
    def process_refund(invoice_id: int, amount: Optional[float], db: Session) -> dict:
        """Process refund for invoice"""
        invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
        if not invoice:
            raise ValueError("Invoice not found")

        refund_amount = amount if amount else invoice.amount

        try:
            # Create Stripe refund
            refund = stripe.Refunds.create(
                payment_intent=invoice.stripe_invoice_id,  # This might need adjustment
                amount=int(refund_amount * 100)  # Convert to cents
            )

            # Update invoice status if full refund
            if refund_amount >= invoice.amount:
                invoice.status = "refunded"

            db.commit()

            return {
                "id": refund["id"],
                "amount": refund_amount,
                "currency": invoice.currency,
                "status": refund["status"]
            }
        except Exception as e:
            raise ValueError(f"Refund failed: {str(e)}")

    @staticmethod
    def update_customer_tax_info(user_id: int, tax_info: dict, db: Session):
        """Update customer tax information in Stripe and DB"""
        user = db.query(User).filter(User.id == user_id).first()
        if not user or not user.stripe_customer_id:
            raise ValueError("User or Stripe customer not found")

        # Update in database
        for key, value in tax_info.items():
            if hasattr(user, key):
                setattr(user, key, value)

        # Update in Stripe
        stripe.Customer.modify(
            user.stripe_customer_id,
            name=tax_info.get("tax_name"),
            address={
                "line1": tax_info.get("tax_address"),
                "country": tax_info.get("tax_country")
            },
            tax_id_data=[{
                "type": "eu_vat" if tax_info.get("tax_country") in ["DE", "FR", "IT", "ES"] else "unknown",
                "value": tax_info.get("tax_id")
            }] if tax_info.get("tax_id") else None
        )

        db.commit()