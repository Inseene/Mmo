import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN, PROXY_URL, SECRET_CODES
from keyboards import get_main_keyboard
from states import Registration, SkillChange

from handlers.registration import (
    start, get_nickname, class_info, confirm_class, back_to_classes
)
from handlers.character import (
    show_character, show_stats, stat_selected, select_amount, confirm_distribute,
    show_items_menu, show_items_category, equip_item, show_resources, show_potions,
    use_potion, show_skills_menu, change_skill_slot, set_skill, show_passive_skills,
    toggle_passive, back_to_character, char_back
)
from handlers.citizens import (
    show_citizens, back_to_city, citizen_info, show_item_info, confirm_buy_item,
    back_to_citizens
)
from handlers.admin import handle_secret_codes, under_development

# Настройка сессии и бота
if PROXY_URL:
    session = AiohttpSession(proxy=PROXY_URL)
else:
    session = AiohttpSession()

bot = Bot(token=BOT_TOKEN, session=session)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Регистрация обработчиков
# Регистрация
dp.message.register(start, Command("start"))
dp.message.register(get_nickname, Registration.waiting_for_nickname)
dp.callback_query.register(class_info, lambda c: c.data.startswith("class_"))
dp.callback_query.register(confirm_class, lambda c: c.data.startswith("confirm_class_"))
dp.callback_query.register(back_to_classes, lambda c: c.data == "back_to_classes")

# Секретные коды
dp.message.register(handle_secret_codes, lambda message: message.text and message.text.startswith("/"))

# Персонаж
dp.message.register(show_character, lambda message: message.text == "📊 Персонаж")
dp.callback_query.register(show_stats, lambda c: c.data == "char_stats")
dp.callback_query.register(stat_selected, lambda c: c.data.startswith("stat_"))
dp.callback_query.register(select_amount, lambda c: c.data.startswith("amount_"))
dp.callback_query.register(confirm_distribute, lambda c: c.data == "confirm_distribute")
dp.callback_query.register(show_items_menu, lambda c: c.data == "char_items")
dp.callback_query.register(show_items_category, lambda c: c.data.startswith("item_"))
dp.callback_query.register(equip_item, lambda c: c.data.startswith("equip_"))
dp.callback_query.register(show_resources, lambda c: c.data == "char_resources")
dp.callback_query.register(show_potions, lambda c: c.data == "resource_potions")
dp.callback_query.register(use_potion, lambda c: c.data.startswith("use_potion_"))
dp.callback_query.register(show_skills_menu, lambda c: c.data == "char_skills")
dp.callback_query.register(change_skill_slot, lambda c: c.data.startswith("skill_change_"))
dp.callback_query.register(set_skill, lambda c: c.data.startswith("choose_skill_"), SkillChange.waiting_for_skill_choice)
dp.callback_query.register(show_passive_skills, lambda c: c.data == "skill_passive")
dp.callback_query.register(toggle_passive, lambda c: c.data.startswith("toggle_passive_"))
dp.callback_query.register(back_to_character, lambda c: c.data == "back_to_character")
dp.callback_query.register(char_back, lambda c: c.data == "char_back")

# Жители
dp.message.register(show_citizens, lambda message: message.text == "👥 Жители")
dp.callback_query.register(back_to_city, lambda c: c.data == "back_to_city")
dp.callback_query.register(citizen_info, lambda c: c.data.startswith("citizen_"))
dp.callback_query.register(show_item_info, lambda c: c.data.startswith("buy_"))
dp.callback_query.register(confirm_buy_item, lambda c: c.data.startswith("confirm_buy_"))
dp.callback_query.register(back_to_citizens, lambda c: c.data == "back_to_citizens")

# Заглушки
dp.message.register(under_development, lambda message: message.text in [
    "🗺️ Путешествие", "🛡️ Клан", "📜 Квесты", "⚙️ Меню", "👫 Друзья", "❓ Помощь"
])

async def main():
    print("✅ Бот запущен и готов к работе!")
    print("🔑 Секретные промокоды:")
    for code in SECRET_CODES:
        print(f"   /{code}")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())