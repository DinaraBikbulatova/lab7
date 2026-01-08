from dataclasses import dataclass, field
from typing import List, Optional
from uuid import uuid4, UUID
from decimal import Decimal
from .value_objects import Money, OrderStatus


@dataclass
class OrderLine:
    product_id: UUID
    product_name: str
    quantity: int
    unit_price: Money

    def __post_init__(self):
        if self.quantity <= 0:
            raise ValueError("Quantity must be positive")

    @property
    def total_price(self) -> Money:
        return self.unit_price * Decimal(self.quantity)


@dataclass
class Order:
    id: UUID = field(default_factory=uuid4)
    customer_id: UUID = field(default_factory=uuid4)
    lines: List[OrderLine] = field(default_factory=list)
    status: str = OrderStatus.CREATED
    _version: int = 0  # для оптимистичной блокировки

    def __post_init__(self):
        self._validate_invariants()

    def _validate_invariants(self):
        """Проверка инвариантов агрегата"""
        # Инвариант 1: итоговая сумма равна сумме строк
        calculated_total = self.calculate_total()

        # Проверяем другие инварианты
        if self.status == OrderStatus.PAID:
            if len(self.lines) == 0:
                raise ValueError("Cannot have empty paid order")

    def add_line(self, line: OrderLine):
        """Добавить строку в заказ"""
        if self.status == OrderStatus.PAID:
            raise ValueError("Cannot modify paid order")
        self.lines.append(line)
        self._version += 1
        self._validate_invariants()

    def remove_line(self, product_id: UUID):
        """Удалить строку из заказа"""
        if self.status == OrderStatus.PAID:
            raise ValueError("Cannot modify paid order")
        self.lines = [line for line in self.lines if line.product_id != product_id]
        self._version += 1
        self._validate_invariants()

    def calculate_total(self) -> Money:
        """Рассчитать итоговую сумму заказа"""
        if not self.lines:
            return Money(Decimal("0"))

        total = self.lines[0].total_price
        for line in self.lines[1:]:
            total = total + line.total_price
        return total

    def pay(self):
        """Оплатить заказ"""
        # Инвариант 1: нельзя оплатить пустой заказ
        if not self.lines:
            raise ValueError("Cannot pay empty order")

        # Инвариант 2: нельзя оплатить заказ повторно
        if self.status == OrderStatus.PAID:
            raise ValueError("Order is already paid")

        # Инвариант 3: итоговая сумма должна быть положительной
        total = self.calculate_total()
        if total.amount <= Decimal("0"):
            raise ValueError("Order total must be positive")

        self.status = OrderStatus.PAID
        self._version += 1

    @property
    def can_be_modified(self) -> bool:
        """Можно ли изменять заказ"""
        return self.status != OrderStatus.PAID