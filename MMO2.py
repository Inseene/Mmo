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

def get_citizens_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🧙 Старейшина Элдрин (Сюжет)", callback_data="citizen_elder")
    )
    builder.row(
        InlineKeyboardButton(text="🏺 Торговец Маркус", callback_data="citizen_merchant")
    )
    builder.row(
        InlineKeyboardButton(text="👧 Мира — Сиротка", callback_data="citizen_mira"),
        InlineKeyboardButton(text="👨 Брат Теодор — Монах", callback_data="citizen_theodore")
    )
    builder.row(
        InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_city")
    )
    return builder.as_markup()

def get_merchant_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🧪 Малое зелье здоровья", callback_data="buy_hp_potion")
    )
    builder.row(
        InlineKeyboardButton(text="💙 Малое зелье маны", callback_data="buy_mana_potion")
    )
    builder.row(
        InlineKeyboardButton(text="🔥 Зелье ярости", callback_data="buy_rage_potion")
    )
    builder.row(
        InlineKeyboardButton(text="⚡ Зелье энергии", callback_data="buy_energy_potion")
    )
    builder.row(
        InlineKeyboardButton(text="🛡️ Зелье стойки", callback_data="buy_stance_potion")
    )
    builder.row(
        InlineKeyboardButton(text="◀️ Назад к жителям", callback_data="back_to_citizens")
    )
    return builder.as_markup()

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
    
    await callback.message.edit_text(
        f"✅ *Регистрация завершена!*\n\n"
        f"Твой никнейм: {nickname}\n"
        f"Твой класс: {chosen_class}\n\n"
        f"Приключение начинается!",
        parse_mode="Markdown"
    )
    
    if class_key == "class_cleric":
        players[user_id]["location"] = "Священный город Люминара"
        
        await callback.message.answer(
            "✨ *СВЯЩЕННЫЙ ГОРОД ЛЮМИНАРА* ✨\n\n"
            "Ты открываешь глаза и видишь перед собой величественный город, залитый мягким золотистым светом. "
            "Высокие шпили соборов из белоснежного мрамора устремляются в небеса, а воздух наполнен "
            "умиротворяющим звоном колоколов и ароматом благовоний.\n\n"
            "Повсюду снуют паломники в светлых одеяниях, а по мостовым медленно шествуют жрецы, "
            "читающие священные манускрипты. В центре площади возвышается гигантская статуя "
            "небесного покровителя, от которой исходит тёплое, исцеляющее сияние.\n\n"
            "Ты чувствуешь, как благословение этого места наполняет твою душу покоем и силой. "
            "Странники со всех концов света приходят сюда в поисках исцеления и мудрости. "
            "Сегодня твой путь начинается именно здесь.",
            parse_mode="Markdown"
        )
        
        await callback.message.answer(
            "📍 *Люминара — Центральная площадь*\n"
            "Куда направишься, путник?",
            reply_markup=get_main_keyboard(),
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

@dp.message(lambda message: message.text == "👥 Жители")
async def show_citizens(message: types.Message):
    user_id = message.from_user.id
    if players.get(user_id, {}).get("location") == "Священный город Люминара":
        await message.answer(
            "👥 *ЖИТЕЛИ ЛЮМИНАРЫ*\n\n"
            "На центральной площади ты видишь несколько человек. К кому подойдёшь?",
            reply_markup=get_citizens_keyboard(),
            parse_mode="Markdown"
        )
    else:
        await message.answer("Вокруг никого нет.")

@dp.callback_query(lambda c: c.data == "back_to_city")
async def back_to_city(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "📍 *Люминара — Центральная площадь*\n"
        "Куда направишься, путник?",
        parse_mode="Markdown"
    )
    await callback.answer()

@dp.callback_query(lambda c: c.data.startswith("citizen_"))
async def citizen_info(callback: types.CallbackQuery):
    citizen_key = callback.data
    
    if citizen_key == "citizen_merchant":
        await callback.message.edit_text(
            "🏺 *ТОРГОВЕЦ МАРКУС*\n\n"
            "Крепкий мужчина средних лет с хитрым прищуром и аккуратной бородкой. Его пояс увешан мешочками с монетами, "
            "а за спиной виднеется тележка с разнообразными товарами — от зелий до диковинных артефактов.\n\n"
            "— Приветствую, добрый странник! Желаешь взглянуть на мои товары?\n\n"
            "*Выбери товар:*",
            reply_markup=get_merchant_keyboard(),
            parse_mode="Markdown"
        )
        await callback.answer()
        return
    
    citizens = {
        "citizen_elder": (
            "🧙 *СТАРЕЙШИНА ЭЛДРИН*\n\n"
            "Седовласый старец с длинной белой бородой, опирающийся на посох, украшенный сияющим кристаллом. "
            "Его глаза, несмотря на возраст, полны мудрости и внутренней силы. Он носит белые одежды с золотой вышивкой "
            "и является верховным жрецом Люминары.\n\n"
            "— А, это ты... Я ждал тебя, путник. Тьма сгущается над нашими землями, и лишь избранный может "
            "остановить её. Но ты пока не готов. Возвращайся, когда наберёшься сил.\n\n"
            "*Основной сюжетный персонаж*"
        ),
        "citizen_mira": (
            "👧 *МИРА — СИРОТКА*\n\n"
            "Девочка лет десяти с большими грустными глазами и растрёпанными светлыми волосами. "
            "Она сидит на ступенях собора, кутаясь в старый плащ, и с надеждой смотрит на прохожих.\n\n"
            "— Господин... госпожа... вы не видели моего котёнка? Он серенький, с белыми лапками. "
            "Я потеряла его возле восточных ворот. Может быть, вы поможете мне найти его?..\n\n"
            "*Побочный квест (пока не работает)*"
        ),
        "citizen_theodore": (
            "👨 *БРАТ ТЕОДОР — МОНАХ*\n\n"
            "Молодой монах в скромной коричневой рясе, с выбритой тонзурой и добрым, слегка встревоженным лицом. "
            "Он постоянно теребит чётки и оглядывается по сторонам.\n\n"
            "— Да пребудет с тобой Свет, путник... Мне нужна помощь. Из монастырской библиотеки пропали "
            "древние свитки. Отец-настоятель будет в ярости, если узнает. Ты не мог бы поискать их в подземельях?\n\n"
            "*Побочный квест (пока не работает)*"
        )
    }
    
    text = citizens.get(citizen_key, "Этот житель пока занят.")
    
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="◀️ Назад к жителям", callback_data="back_to_citizens"))
    
    await callback.message.edit_text(
        text,
        reply_markup=builder.as_markup(),
        parse_mode="Markdown"
    )
    await callback.answer()

@dp.callback_query(lambda c: c.data.startswith("buy_"))
async def buy_item(callback: types.CallbackQuery):
    items = {
        "buy_hp_potion": ("🧪 Малое зелье здоровья", "+50 HP", "30 золота"),
        "buy_mana_potion": ("💙 Малое зелье маны", "+20 маны", "40 золота"),
        "buy_rage_potion": ("🔥 Зелье ярости", "+30 ярости", "30 золота"),
        "buy_energy_potion": ("⚡ Зелье энергии", "+30 энергии", "30 золота"),
        "buy_stance_potion": ("🛡️ Зелье стойки", "+30 стойки", "30 золота")
    }
    
    item = items.get(callback.data, ("Неизвестный предмет", "", ""))
    
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="◀️ Назад к товарам", callback_data="citizen_merchant"))
    
    await callback.message.edit_text(
        f"*{item[0]}*\n\n"
        f"Эффект: {item[1]}\n"
        f"Цена: {item[2]}\n\n"
        f"❌ *Покупка пока недоступна*\n"
        f"Торговец разводит руками:\n"
        f"— Прости, странник, торговля ещё не открыта. Заходи позже!",
        reply_markup=builder.as_markup(),
        parse_mode="Markdown"
    )
    await callback.answer()

@dp.callback_query(lambda c: c.data == "back_to_citizens")
async def back_to_citizens(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "👥 *ЖИТЕЛИ ЛЮМИНАРЫ*\n\n"
        "На центральной площади ты видишь несколько человек. К кому подойдёшь?",
        reply_markup=get_citizens_keyboard(),
        parse_mode="Markdown"
    )
    await callback.answer()

async def main():
    print("✅ Бот запущен и готов к работе!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
