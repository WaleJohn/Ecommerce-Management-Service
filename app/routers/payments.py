from fastapi import APIRouter, HTTPException, status

from app.models import OrderStatus, Payment, PaymentCreate, PaymentStatus, PaymentUpdate
from app.repository import now, store

router = APIRouter(prefix="/payments", tags=["payments"])


@router.post("", response_model=Payment, status_code=status.HTTP_201_CREATED)
def create_payment(payload: PaymentCreate) -> Payment:
    order = store.orders.get(payload.order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found.")

    if round(payload.amount, 2) != round(order.total_amount, 2):
        raise HTTPException(status_code=422, detail="Payment amount must match the order total.")

    payment = Payment(**payload.model_dump())
    store.payments[payment.id] = payment
    return payment


@router.get("", response_model=list[Payment])
def list_payments(order_id: str | None = None) -> list[Payment]:
    payments = list(store.payments.values())
    if order_id is not None:
        payments = [payment for payment in payments if payment.order_id == order_id]
    return payments


@router.get("/{payment_id}", response_model=Payment)
def get_payment(payment_id: str) -> Payment:
    payment = store.payments.get(payment_id)
    if payment is None:
        raise HTTPException(status_code=404, detail="Payment not found.")
    return payment


@router.patch("/{payment_id}", response_model=Payment)
def update_payment(payment_id: str, payload: PaymentUpdate) -> Payment:
    payment = store.payments.get(payment_id)
    if payment is None:
        raise HTTPException(status_code=404, detail="Payment not found.")

    updated_payment = payment.model_copy(
        update={
            "status": payload.status,
            "external_reference": payload.external_reference,
            "updated_at": now(),
        }
    )
    store.payments[payment_id] = updated_payment

    if payload.status == PaymentStatus.captured:
        order = store.orders[payment.order_id]
        store.orders[payment.order_id] = order.model_copy(
            update={"status": OrderStatus.paid, "updated_at": now()}
        )

    return updated_payment
