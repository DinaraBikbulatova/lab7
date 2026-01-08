from dataclasses import dataclass
from typing import ClassVar
from decimal import Decimal


@dataclass(frozen=True)
class Money:
    amount: Decimal
    currency: str = "USD"

    def __post_init__(self):
        if self.amount < Decimal("0"):
            raise ValueError("Money amount cannot be negative")

    def __add__(self, other: "Money") -> "Money":
        if self.currency != other.currency:
            raise ValueError("Cannot add money with different currencies")
        return Money(self.amount + other.amount, self.currency)

    def __sub__(self, other: "Money") -> "Money":
        if self.currency != other.currency:
            raise ValueError("Cannot subtract money with different currencies")
        return Money(self.amount - other.amount, self.currency)

    def __mul__(self, multiplier: Decimal) -> "Money":
        return Money(self.amount * multiplier, self.currency)

    def __repr__(self):
        return f"Money({self.amount:.2f} {self.currency})"


class OrderStatus:
    CREATED: ClassVar[str] = "created"
    PAID: ClassVar[str] = "paid"
    CANCELLED: ClassVar[str] = "cancelled"