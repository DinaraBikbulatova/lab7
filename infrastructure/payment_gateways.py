from uuid import UUID
from domain.value_objects import Money
from domain.repositories import PaymentGateway


class FakePaymentGateway(PaymentGateway):
    """Фейковый платежный шлюз для тестирования"""

    def __init__(self, always_succeed: bool = True):
        self.always_succeed = always_succeed
        self.payment_history = []

    def charge(self, order_id: UUID, amount: Money) -> bool:
        """Имитация списания денег"""
        self.payment_history.append({
            "order_id": order_id,
            "amount": amount,
            "timestamp": "2024-01-01T00:00:00Z"
        })
        return self.always_succeed

    def get_payment_count(self) -> int:
        """Получить количество выполненных платежей"""
        return len(self.payment_history)