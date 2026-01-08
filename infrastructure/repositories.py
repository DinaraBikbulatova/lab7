from typing import Dict, Optional
from uuid import UUID
from domain.entities import Order
from domain.repositories import OrderRepository


class InMemoryOrderRepository(OrderRepository):
    """In-memory реализация репозитория заказов"""

    def __init__(self):
        self._orders: Dict[UUID, Order] = {}

    def get_by_id(self, order_id: UUID) -> Optional[Order]:
        """Получить заказ по ID"""
        return self._orders.get(order_id)

    def save(self, order: Order) -> None:
        """Сохранить заказ"""
        self._orders[order.id] = order

    def clear(self):
        """Очистить репозиторий (для тестов)"""
        self._orders.clear()