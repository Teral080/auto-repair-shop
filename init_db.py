import asyncio
from models import create_all_tables

async def main():
    print("Создаём таблицы...")
    await create_all_tables()
    print("✅ Таблицы успешно созданы!")

if __name__ == "__main__":
    asyncio.run(main())