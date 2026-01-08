from uuid import uuid4
from decimal import Decimal
from domain.value_objects import Money
from domain.entities import Order, OrderLine
from infrastructure.repositories import InMemoryOrderRepository
from infrastructure.payment_gateways import FakePaymentGateway
from application.use_cases import PayOrderUseCase


def main():
    print("=== Система оплаты заказов ===\n")
    
    # Инициализация зависимостей
    order_repo = InMemoryOrderRepository()
    payment_gateway = FakePaymentGateway()
    pay_order_use_case = PayOrderUseCase(order_repo, payment_gateway)
    
    # Создание заказа
    order = Order(customer_id=uuid4())
    
    # Добавление товаров
    order.add_line(OrderLine(
        product_id=uuid4(),
        product_name="Ноутбук",
        quantity=1,
        unit_price=Money(Decimal("1500.00"))
    ))
    
    order.add_line(OrderLine(
        product_id=uuid4(),
        product_name="Наушники",
        quantity=2,
        unit_price=Money(Decimal("100.00"))
    ))
    
    # Сохранение заказа
    order_repo.save(order)
    print(f"Создан заказ #{order.id}")
    print(f"Итоговая сумма: {order.calculate_total()}")
    
    # Оплата заказа
    print("\nПытаемся оплатить заказ...")
    success, message = pay_order_use_case.execute(order.id)
    
    if success:
        print(f"✓ {message}")
        updated_order = order_repo.get_by_id(order.id)
        print(f"Статус заказа: {updated_order.status}")
    else:
        print(f"✗ {message}")
    
    # Статистика платежей
    print(f"\nКоличество выполненных платежей: {payment_gateway.get_payment_count()}")


if __name__ == "__main__":
    main()
