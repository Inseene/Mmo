import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

PROXY_URL = None

if PROXY_URL:
    session = AiohttpSession(proxy=PROXY_URL)
else:
    session = AiohttpSession()

bot = Bot(token="8675520138:AAF_I6r08Wi0geVIaieeLRtLriF783Nbk60", session=session)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

players = {}

class Registration(StatesGroup):
    waiting_for_nickname = State()

def get_main_keyboard():
    builder = ReplyKeyboardBuilder()
    builder.row(
        KeyboardButton(text="🗺️ Путешествие"),
        KeyboardButton(text="👥 Жители")
    )
    builder.row(
        KeyboardButton(text="📊 Персонаж"),
        KeyboardButton(text="🛡️ Клан")
    )
    builder.row(
        KeyboardButton(text="📜 Квесты"),
        KeyboardButton(text="⚙️ Меню")
    )
    builder.row(
        KeyboardButton(text="👫 Друзья"),
        KeyboardButton(text="❓ Помощь")
    )
    return builder.as_markup(resize_keyboard=True)

@dp.message(Command("start"))
async def start(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    if user_id not in players:
        players[user_id] = {
            "tg_id": user_id,
            "nickname": None,
            "class": None,
            "registered": False,
            "location": None
        }
        await message.answer("🎮 Приветствую, странник! Назови свой никнейм:")
        await state.set_state(Registration.waiting_for_nickname)
    else:
        await message.answer("Ты уже зарегистрирован!")

@dp.message(Registration.waiting_for_nickname)
async def get_nickname(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    nickname = message.text.strip()
    
    if len(nickname) < 3:
        await message.answer("❌ Никнейм должен быть не короче 3 символов. Попробуй снова:")
        return
    
    if len(nickname) > 16:
        await message.answer("❌ Никнейм должен быть не длиннее 16 символов. Попробуй снова:")
        return
    
    players[user_id]["nickname"] = nickname
    
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="⚔️ Воин", callback_data="class_warrior"),
        InlineKeyboardButton(text="🔥 Маг", callback_data="class_mage")
    )
    builder.row(
        InlineKeyboardButton(text="🏹 Лучник", callback_data="class_archer"),
        InlineKeyboardButton(text="💚 Клерик", callback_data="class_cleric")
    )
    
    await message.answer(
        f"✨ Приятно познакомиться, {nickname}!\n\n"
        "Выбери свой класс:",
        reply_markup=builder.as_markup()
    )
    await state.clear()

@dp.callback_query(lambda c: c.data.startswith("class_"))
async def class_info(callback: types.CallbackQuery):
    class_descriptions = {
        "class_warrior": (
            "⚔️ *ВОИН*\n\n"
            "Закалённый в бесчисленных битвах боец, чья стальная воля крепче любой брони. "
            "Стоит несокрушимой стеной между товарищами и самой смертью, принимая на себя удары, "
            "что сломили бы любого другого. Его клинок поёт песню доблести, а щит хранит тепло родных земель.\n\n"
            "На 15 уровне может стать рыцарем или разбойником."
        ),
        "class_mage": (
            "🔥 *МАГ*\n\n"
            "Повелитель тайных сил, чей разум пронзает завесу мироздания. "
            "В его жилах течёт не кровь, а чистая магия, готовая обрушиться на врагов испепеляющим пламенем "
            "или окутать союзников спасительной пеленой. Там, где бессильна сталь, говорит заклинание.\n\n"
            "На 15 уровне может стать волшебником или некромантом."
        ),
        "class_archer": (
            "🏹 *ЛУЧНИК*\n\n"
            "Мастер смертоносной точности, сливающийся с тенями лесов и руин. "
            "Каждая его стрела — приговор, подписанный задолго до того, как враг поймёт, что уже мёртв. "
            "Он не ищет славы в лобовой атаке — его удел это стремительный танец смерти на расстоянии.\n\n"
            "На 15 уровне может стать инженером или сталкером."
        ),
        "class_cleric": (
            "💚 *КЛЕРИК*\n\n"
            "Избранник высших сил, несущий свет надежды в самые тёмные уголки мира. "
            "Его молитвы исцеляют раны, что не подвластны времени, а благословения заставляют клинки союзников "
            "сиять праведным гневом. Там, где ступает клерик, отступает сама тьма.\n\n"
            "На 15 уровне может стать жрецом или паладином."
        )
    }
    
    description = class_descriptions.get(callback.data, "Описание класса отсутствует.")
    
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="✅ Выбрать этот класс", callback_data=f"confirm_{callback.data}"))
    builder.row(InlineKeyboardButton(text="◀️ Назад к выбору", callback_data="back_to_classes"))
    
    await callback.message.edit_text(
        description,
        reply_markup=builder.as_markup(),
        parse_mode="Markdown"
    )
    await callback.answer()

@dp.callback_query(lambda c: c.data.startswith("confirm_class_"))
async def confirm_class(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    class_key = callback.data.replace("confirm_", "")
    
    class_map = {
        "class_warrior": "⚔️ Воин",
        "class_mage": "🔥 Маг",
        "class_archer": "🏹 Лучник",
        "class_cleric": "💚 Клерик"
    }
    
    chosen_class = class_map[class_key]
    players[user_id]["class"] = chosen_class
    players[user_id]["registered"] = True
    nickname = players[user_id]["nickname"]
    
    if class_key == "class_cleric":
        players[user_id]["location"] = "Священный город Люминара"
        
        city_description = (
            "✨ *СВЯЩЕННЫЙ ГОРОД ЛЮМИНАРА* ✨\n\n"
            "Ты открываешь глаза и видишь перед собой величественный город, залитый мягким золотистым светом. "
            "Высокие шпили соборов из белоснежного мрамора устремляются в небеса, а воздух наполнен "
            "умиротворяющим звоном колоколов и ароматом благовоний.\n\n"
            "Повсюду снуют паломники в светлых одеяниях, а по мостовым медленно шествуют жрецы, "
            "читающие священные манускрипты. В центре площади возвышается гигантская статуя "
            "небесного покровителя, от которой исходит тёплое, исцеляющее сияние.\n\n"
            "Ты чувствуешь, как благословение этого места наполняет твою душу покоем и силой. "
            "Странники со всех концов света приходят сюда в поисках исцеления и мудрости. "
            "Сегодня твой путь начинается именно здесь."
        )
        
        await callback.message.edit_text(
            f"✅ *Регистрация завершена!*\n\n"
            f"Твой никнейм: {nickname}\n"
            f"Твой класс: {chosen_class}\n\n"
            f"{city_description}",
            parse_mode="Markdown"
        )
        
        await callback.message.answer(
            "📍 *Люминара — Центральная площадь*\n"
            "Куда направишься, путник?",
            reply_markup=get_main_keyboard(),
            parse_mode="Markdown"
        )
    else:
        await callback.message.edit_text(
            f"✅ *Регистрация завершена!*\n\n"
            f"Твой никнейм: {nickname}\n"
            f"Твой класс: {chosen_class}\n\n"
            f"Приключение начинается!",
            parse_mode="Markdown"
        )
    
    await callback.answer()

@dp.callback_query(lambda c: c.data == "back_to_classes")
async def back_to_classes(callback: types.CallbackQuery):
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="⚔️ Воин", callback_data="class_warrior"),
        InlineKeyboardButton(text="🔥 Маг", callback_data="class_mage")
    )
    builder.row(
        InlineKeyboardButton(text="🏹 Лучник", callback_data="class_archer"),
        InlineKeyboardButton(text="💚 Клерик", callback_data="class_cleric")
    )
    
    await callback.message.edit_text(
        "Выбери свой класс:",
        reply_markup=builder.as_markup()
    )
    await callback.answer()

async def main():
    print("✅ Бот запущен и готов к работе!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
