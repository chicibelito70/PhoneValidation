from app.database import SessionLocal, engine, Base
from app.models import Plan
import os

def create_initial_plans():
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    plans = [
        {
            "name": "free",
            "stripe_price_id": os.getenv("STRIPE_PRICE_FREE", "price_free"),
            "price": 0.0,
            "currency": "usd",
            "interval": "month",
            "daily_limit": 100,
            "monthly_limit": 1000,
            "is_active": True
        },
        {
            "name": "pro",
            "stripe_price_id": os.getenv("STRIPE_PRICE_PRO", "price_pro"),
            "price": 29.99,
            "currency": "usd",
            "interval": "month",
            "daily_limit": 10000,
            "monthly_limit": 100000,
            "is_active": True
        },
        {
            "name": "enterprise",
            "stripe_price_id": os.getenv("STRIPE_PRICE_ENTERPRISE", "price_enterprise"),
            "price": 99.99,
            "currency": "usd",
            "interval": "month",
            "daily_limit": 0,  # Unlimited
            "monthly_limit": 0,
            "is_active": True
        }
    ]
    for plan_data in plans:
        plan = db.query(Plan).filter(Plan.name == plan_data["name"]).first()
        if not plan:
            plan = Plan(**plan_data)
            db.add(plan)
    db.commit()
    db.close()

if __name__ == "__main__":
    create_initial_plans()