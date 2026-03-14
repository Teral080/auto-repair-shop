import pytest
from app import create_app

# --- Настройка тестового окружения ---

@pytest.fixture
def app_instance():
    """Создает приложение для тестов."""
    app = create_app()
    app.config.update({
        "TESTING": True,
    })
    return app

@pytest.fixture
def test_client(app_instance):
    """Создает тестовый клиент для имитации запросов."""
    return app_instance.test_client()


# --- ТЕСТ 1: Доступ к закрытому разделу (Безопасность) ---

@pytest.mark.asyncio
async def test_unauthorized_access_redirect(test_client):
    # Пытаемся зайти на страницу клиентов без логина
    # В routes.py у тебя прописан путь '/clients' (маленькими буквами)
    response = await test_client.get('/clients')
    
    # Ожидаем, что сработает защита и нас перенаправит (код 302)
    assert response.status_code == 302
    # Проверяем, что перенаправляет на главную (или страницу входа)
    assert '/' in response.location 


# --- ТЕСТ 2: Формирование заказа с ошибкой (Транзакции/Склад) ---

@pytest.mark.asyncio
async def test_create_order_insufficient_stock(app_instance):
    from routes import create_order
    from models import async_session, Part
    
    async with app_instance.app_context():
        # 1. Имитируем ситуацию: в базу добавляется запчасть, которой НЕТ в наличии (stock=0)
        async with async_session() as s:
            test_part = Part(name="Деталь без остатка", price=1000, stock=0)
            s.add(test_part)
            await s.commit()
            await s.refresh(test_part)
            part_id = test_part.id

        # 2. Пытаемся создать заказ с этой деталью и ОЖИДАЕМ ошибку ValueError
        with pytest.raises(ValueError) as excinfo:
            await create_order(
                client_id=1, 
                user_id=1, 
                description="Тест нехватки деталей", 
                part_ids=[str(part_id)]
            )
        
        # 3. Убеждаемся, что ошибка именно та, которую мы написали в routes.py
        assert "Недостаточно запчастей" in str(excinfo.value)