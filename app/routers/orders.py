from fastapi import APIRouter, HTTPException, status

from app.models import Order, OrderCreate, OrderStatus, OrderUpdate
from app.repository import now, store

router = APIRouter(prefix="/orders", tags=["orders"])


def calculate_total(payload: OrderCreate) -> float:
    return round(sum(item.quantity * item.unit_price for item in payload.items), 2)


@router.post("", response_model=Order, status_code=status.HTTP_201_CREATED)
def create_order(payload: OrderCreate) -> Order:
    if payload.user_id not in store.users:
        raise HTTPException(status_code=404, detail="User not found.")

    order = Order(
        user_id=payload.user_id,
        items=payload.items,
        total_amount=calculate_total(payload),
    )
    store.orders[order.id] = order
    return order


@router.get("", response_model=list[Order])
def list_orders(user_id: str | None = None) -> list[Order]:
    orders = list(store.orders.values())
    if user_id is not None:
        orders = [order for order in orders if order.user_id == user_id]
    return orders


@router.get("/{order_id}", response_model=Order)
def get_order(order_id: str) -> Order:
    order = store.orders.get(order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found.")
    return order


@router.patch("/{order_id}", response_model=Order)
def update_order(order_id: str, payload: OrderUpdate) -> Order:
    order = store.orders.get(order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found.")

    if order.status == OrderStatus.cancelled and payload.status != OrderStatus.cancelled:
        raise HTTPException(status_code=409, detail="Cancelled orders cannot be reopened.")

    updated_order = order.model_copy(update={"status": payload.status, "updated_at": now()})
    store.orders[order_id] = updated_order
    return updated_order


@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_order(order_id: str) -> None:
    if order_id not in store.orders:
        raise HTTPException(status_code=404, detail="Order not found.")
    del store.orders[order_id]
