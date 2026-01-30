from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class UserCreate(BaseModel):
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class UserTaxInfo(BaseModel):
    tax_name: Optional[str] = None
    tax_address: Optional[str] = None
    tax_country: Optional[str] = None
    tax_id: Optional[str] = None

class UserUpdate(BaseModel):
    tax_name: Optional[str] = None
    tax_address: Optional[str] = None
    tax_country: Optional[str] = None
    tax_id: Optional[str] = None

class Token(BaseModel):
    access_token: str
    token_type: str

class PlanBase(BaseModel):
    name: str
    price: float
    currency: str
    interval: str
    daily_limit: int
    monthly_limit: int

class PlanCreate(PlanBase):
    pass

class Plan(PlanBase):
    id: int
    stripe_price_id: str
    is_active: bool

    class Config:
        from_attributes = True

class SubscriptionBase(BaseModel):
    plan_id: int

class SubscriptionCreate(SubscriptionBase):
    pass

class Subscription(SubscriptionBase):
    id: int
    user_id: int
    stripe_subscription_id: str
    status: str
    current_period_start: datetime
    current_period_end: datetime
    cancel_at_period_end: bool

    class Config:
        from_attributes = True

class APIKeyCreate(BaseModel):
    plan_id: Optional[int] = None

class APIKeyResponse(BaseModel):
    id: int
    key_prefix: str
    plan_id: Optional[int]
    status: str
    daily_usage: int
    monthly_usage: int

class CheckoutSessionCreate(BaseModel):
    plan_id: int

class CheckoutSessionResponse(BaseModel):
    checkout_url: str

class UsageResponse(BaseModel):
    daily_usage: int
    monthly_usage: int
    plan: str
    status: str

class PaymentResponse(BaseModel):
    id: int
    amount: float
    currency: str
    status: str
    description: str
    created_at: datetime

class SubscriptionResponse(BaseModel):
    id: int
    plan: Plan
    status: str
    current_period_start: datetime
    current_period_end: datetime
    cancel_at_period_end: bool

class ChangePlanRequest(BaseModel):
    new_plan_id: int

class InvoiceItemResponse(BaseModel):
    id: int
    description: str
    amount: float
    quantity: int
    period_start: Optional[datetime]
    period_end: Optional[datetime]

class InvoiceResponse(BaseModel):
    id: int
    stripe_invoice_id: str
    amount: float
    currency: str
    status: str
    pdf_url: Optional[str]
    period_start: Optional[datetime]
    period_end: Optional[datetime]
    issued_at: datetime
    paid_at: Optional[datetime]
    items: list[InvoiceItemResponse]

    class Config:
        from_attributes = True

class RefundRequest(BaseModel):
    invoice_id: int
    amount: Optional[float] = None  # None for full refund

class RefundResponse(BaseModel):
    id: str
    amount: float
    currency: str
    status: str