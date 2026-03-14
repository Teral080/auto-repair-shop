import pytest
from app import create_app

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