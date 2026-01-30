from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base
from .routes.auth import router as auth_router
from .routes.api_keys import router as api_keys_router
from .routes.billing import router as billing_router
from .routes.dashboard import router as dashboard_router
from .routes.phone import router as phone_router
from .middlewares import api_key_middleware

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Phone Validation SaaS API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add API key middleware to protected routes
app.middleware("http")(api_key_middleware)

app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(api_keys_router, prefix="/api-keys", tags=["API Keys"])
app.include_router(billing_router, prefix="/billing", tags=["Billing"])
app.include_router(dashboard_router, prefix="/dashboard", tags=["Dashboard"])
app.include_router(phone_router, prefix="/phone", tags=["Phone Validation"])

@app.get("/")
def read_root():
    return {"message": "Phone Validation SaaS API"}