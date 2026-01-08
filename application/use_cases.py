from typing import Tuple
from uuid import UUID
from decimal import Decimal
from domain.value_objects import Money
from domain.entities import Order
from domain.repositories import OrderRepository, PaymentGateway


class PayOrderUseCase:
    """Use case для оплаты заказа"""

    def __init__(
            self,
            order_repository: OrderRepository,
            payment_gateway: PaymentGateway
    ):
        self.order_repository = order_repository
        self.payment_gateway = payment_gateway

    def execute(self, order_id: UUID) -> Tuple[bool, str]:
        """
        Выполнить оплату заказа

        Returns:
            Tuple[bool, str]: (успех, сообщение)
        """
        # 1. Загружаем заказ
        order = self.order_repository.get_by_id(order_id)
        if not order:
            return False, f"Order {order_id} not found"

        try:
            # 2. Проверяем можно ли оплатить (но НЕ оплачиваем ещё)
            if not order.lines:
                return False, "Cannot pay empty order"
            if order.status == "paid":
                return False, "Order is already paid"
            
            total_amount = order.calculate_total()
            if total_amount.amount <= Decimal("0"):
                return False, "Order total must be positive"

            # 3. Вызываем платежный шлюз
            payment_success = self.payment_gateway.charge(order_id, total_amount)

            if not payment_success:
                return False, "Payment failed"

            # 4. Только если платеж успешен - оплачиваем заказ
            order.pay()

            # 5. Сохраняем заказ
            self.order_repository.save(order)

            return True, f"Order {order_id} paid successfully"

        except ValueError as e:
            return False, str(e)
