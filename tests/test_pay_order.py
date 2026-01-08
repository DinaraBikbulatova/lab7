import pytest
from uuid import uuid4, UUID
from decimal import Decimal
from domain.value_objects import Money, OrderStatus
from domain.entities import Order, OrderLine
from infrastructure.repositories import InMemoryOrderRepository
from infrastructure.payment_gateways import FakePaymentGateway
from application.use_cases import PayOrderUseCase


class TestPayOrderUseCase:

    @pytest.fixture
    def order_repository(self):
        return InMemoryOrderRepository()

    @pytest.fixture
    def payment_gateway(self):
        return FakePaymentGateway(always_succeed=True)

    @pytest.fixture
    def use_case(self, order_repository, payment_gateway):
        return PayOrderUseCase(order_repository, payment_gateway)

    @pytest.fixture
    def sample_order(self):
        """Создать тестовый заказ с товарами"""
        order = Order()
        order.add_line(OrderLine(
            product_id=uuid4(),
            product_name="Laptop",
            quantity=1,
            unit_price=Money(Decimal("1000.00"))
        ))
        order.add_line(OrderLine(
            product_id=uuid4(),
            product_name="Mouse",
            quantity=2,
            unit_price=Money(Decimal("25.00"))
        ))
        return order

    def test_successful_payment(self, use_case, order_repository, sample_order):
        """Тест успешной оплаты корректного заказа"""
        # Arrange
        order_repository.save(sample_order)

        # Act
        success, message = use_case.execute(sample_order.id)

        # Assert
        assert success is True
        assert "successfully" in message
        assert order_repository.get_by_id(sample_order.id).status == OrderStatus.PAID

    def test_payment_empty_order(self, use_case, order_repository):
        """Тест ошибки при оплате пустого заказа"""
        # Arrange
        empty_order = Order()
        order_repository.save(empty_order)

        # Act
        success, message = use_case.execute(empty_order.id)

        # Assert
        assert success is False
        assert "empty" in message.lower() or "cannot pay" in message.lower()

    def test_double_payment_error(self, use_case, order_repository, sample_order):
        """Тест ошибки при повторной оплате"""
        # Arrange
        order_repository.save(sample_order)

        # Первая оплата (должна пройти)
        success1, _ = use_case.execute(sample_order.id)
        assert success1 is True

        # Act: Вторая попытка оплаты
        success2, message = use_case.execute(sample_order.id)

        # Assert
        assert success2 is False
        assert "already paid" in message.lower()

    def test_cannot_modify_after_payment(self, use_case, order_repository, sample_order):
        """Тест невозможности изменения заказа после оплаты"""
        # Arrange
        order_repository.save(sample_order)

        # Оплачиваем заказ
        success, _ = use_case.execute(sample_order.id)
        assert success is True

        paid_order = order_repository.get_by_id(sample_order.id)

        # Act & Assert: Попытка добавить товар в оплаченный заказ
        with pytest.raises(ValueError, match="Cannot modify paid order"):
            paid_order.add_line(OrderLine(
                product_id=uuid4(),
                product_name="Keyboard",
                quantity=1,
                unit_price=Money(Decimal("50.00"))
            ))

    def test_correct_total_calculation(self, sample_order):
        """Тест корректного расчёта итоговой суммы"""
        # Act
        total = sample_order.calculate_total()

        # Assert
        # Laptop: 1000 + Mouse: 2 * 25 = 1050
        expected_total = Money(Decimal("1050.00"))
        assert total.amount == expected_total.amount
        assert total.currency == expected_total.currency

    def test_payment_gateway_failure(self, order_repository, sample_order):
        """Тест неудачной оплаты через платежный шлюз"""
        # Arrange
        failing_gateway = FakePaymentGateway(always_succeed=False)
        use_case = PayOrderUseCase(order_repository, failing_gateway)
        order_repository.save(sample_order)

        # Act
        success, message = use_case.execute(sample_order.id)

        # Assert
        assert success is False
        assert "failed" in message.lower()
        assert order_repository.get_by_id(sample_order.id).status == OrderStatus.CREATED


if __name__ == "__main__":
    # Запуск тестов
    print("Running tests...")

    # Создаем тестовые объекты
    repo = InMemoryOrderRepository()
    gateway = FakePaymentGateway()
    use_case = PayOrderUseCase(repo, gateway)

    # Тест 1: Корректный заказ
    order = Order()
    order.add_line(OrderLine(
        product_id=uuid4(),
        product_name="Test Product",
        quantity=2,
        unit_price=Money(Decimal("100.00"))
    ))
    repo.save(order)

    success, message = use_case.execute(order.id)
    print(f"Test 1 - Successful payment: {success}, message: {message}")

    # Тест 2: Пустой заказ
    empty_order = Order()
    repo.save(empty_order)

    success, message = use_case.execute(empty_order.id)
    print(f"Test 2 - Empty order payment: {success}, message: {message}")

    print("\nAll tests completed!")