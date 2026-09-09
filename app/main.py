from fastapi import FastAPI

from app.routers import orders, payments, users


app = FastAPI(
    title="Ecommerce Management Service",
    description="User, order, and payment tracking APIs for an ecommerce app.",
    version="0.1.0",
)

app.include_router(users.router)
app.include_router(orders.router)
app.include_router(payments.router)


@app.get("/health", tags=["health"])
def health_check() -> dict[str, str]:
    return {"status": "ok"}
