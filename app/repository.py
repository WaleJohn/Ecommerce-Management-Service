from datetime import datetime, timezone

from app.models import Order, Payment, User


def now() -> datetime:
    return datetime.now(timezone.utc)


class InMemoryStore:
    def __init__(self) -> None:
        self.users: dict[str, User] = {}
        self.orders: dict[str, Order] = {}
        self.payments: dict[str, Payment] = {}

    def reset(self) -> None:
        self.users.clear()
        self.orders.clear()
        self.payments.clear()


store = InMemoryStore()
