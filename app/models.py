from datetime import datetime, timezone
from enum import Enum
from uuid import uuid4

from pydantic import BaseModel, EmailStr, Field, PositiveFloat, field_validator


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def new_id() -> str:
    return str(uuid4())


class UserStatus(str, Enum):
    active = "active"
    disabled = "disabled"


class OrderStatus(str, Enum):
    pending = "pending"
    paid = "paid"
    shipped = "shipped"
    cancelled = "cancelled"


class PaymentStatus(str, Enum):
    pending = "pending"
    authorized = "authorized"
    captured = "captured"
    failed = "failed"
    refunded = "refunded"


class PaymentProvider(str, Enum):
    stripe = "stripe"
    paypal = "paypal"
    manual = "manual"


class UserCreate(BaseModel):
    email: EmailStr
    full_name: str = Field(..., min_length=1, max_length=120)
    status: UserStatus = UserStatus.active


class UserUpdate(BaseModel):
    email: EmailStr | None = None
    full_name: str | None = Field(default=None, min_length=1, max_length=120)
    status: UserStatus | None = None


class User(UserCreate):
    id: str = Field(default_factory=new_id)
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)


class OrderItem(BaseModel):
    sku: str = Field(..., min_length=1, max_length=80)
    name: str = Field(..., min_length=1, max_length=160)
    quantity: int = Field(..., gt=0)
    unit_price: PositiveFloat


class OrderCreate(BaseModel):
    user_id: str
    items: list[OrderItem] = Field(..., min_length=1)


class OrderUpdate(BaseModel):
    status: OrderStatus


class Order(BaseModel):
    id: str = Field(default_factory=new_id)
    user_id: str
    items: list[OrderItem]
    status: OrderStatus = OrderStatus.pending
    total_amount: float
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)


class PaymentCreate(BaseModel):
    order_id: str
    amount: PositiveFloat
    provider: PaymentProvider = PaymentProvider.manual
    external_reference: str | None = Field(default=None, max_length=160)

    @field_validator("external_reference")
    @classmethod
    def normalize_reference(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip()
        return normalized or None


class PaymentUpdate(BaseModel):
    status: PaymentStatus
    external_reference: str | None = Field(default=None, max_length=160)


class Payment(BaseModel):
    id: str = Field(default_factory=new_id)
    order_id: str
    amount: float
    provider: PaymentProvider
    status: PaymentStatus = PaymentStatus.pending
    external_reference: str | None = None
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)
