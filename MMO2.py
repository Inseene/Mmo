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

class StatDistribution(StatesGroup):
    waiting_for_stat = State()
    waiting_for_amount = State()

class SkillChange(StatesGroup):
    waiting_for_skill_slot = State()
    waiting_for_skill_choice = State()

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

def get_character_menu_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="📈 Характеристики", callback_data="char_stats"),
        InlineKeyboardButton(text="🎒 Предметы", callback_data="char_items")
    )
    builder.row(
        InlineKeyboardButton(text="📦 Ресурсы", callback_data="char_resources"),
        InlineKeyboardButton(text="✨ Навыки", callback_data="char_skills")
    )
    builder.row(
        InlineKeyboardButton(text="◀️ Назад", callback_data="char_back")
    )
    return builder.as_markup()

def get_stats_keyboard(player_class):
    builder = InlineKeyboardBuilder()
    if "Воин" in player_class or "Лучник" in player_class:
        builder.row(InlineKeyboardButton(text="💪 Сила", callback_data="stat_strength"))
    else:
        builder.row(InlineKeyboardButton(text="📚 Интеллект", callback_data="stat_intelligence"))
    builder.row(
        InlineKeyboardButton(text="❤️ Выносливость", callback_data="stat_vitality"),
        InlineKeyboardButton(text="🏃 Ловкость", callback_data="stat_agility")
    )
    builder.row(
        InlineKeyboardButton(text="🔮 Интуиция", callback_data="stat_intuition")
    )
    builder.row(
        InlineKeyboardButton(text="✅ Распределить", callback_data="stat_distribute"),
        InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_character")
    )
    return builder.as_markup()

def get_items_category_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="⚔️ Оружие", callback_data="item_weapons"),
        InlineKeyboardButton(text="⛑️ Шлемы", callback_data="item_helmets")
    )
    builder.row(
        InlineKeyboardButton(text="🛡️ Доспехи", callback_data="item_armors"),
        InlineKeyboardButton(text="🧤 Перчатки", callback_data="item_gloves")
    )
    builder.row(
        InlineKeyboardButton(text="👢 Сапоги", callback_data="item_boots"),
        InlineKeyboardButton(text="💍 Кольца", callback_data="item_rings")
    )
    builder.row(
        InlineKeyboardButton(text="📿 Амулеты", callback_data="item_amulets")
    )
    builder.row(
        InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_character")
    )
    return builder.as_markup()

def get_skills_menu_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="1️⃣ Сменить 1 навык", callback_data="skill_change_1"),
        InlineKeyboardButton(text="2️⃣ Сменить 2 навык", callback_data="skill_change_2")
    )
    builder.row(
        InlineKeyboardButton(text="3️⃣ Сменить 3 навык", callback_data="skill_change_3"),
        InlineKeyboardButton(text="4️⃣ Сменить 4 навык", callback_data="skill_change_4")
    )
    builder.row(
        InlineKeyboardButton(text="⭐ Пассивные навыки", callback_data="skill_passive")
    )
    builder.row(
        InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_character")
    )
    return builder.as_markup()

def init_new_player(user_id, nickname, chosen_class):
    """Инициализация нового игрока"""
    base_stats = {}
    combat_stats = {}
    
    if "Воин" in chosen_class:
        base_stats = {"strength": 8, "intelligence": 2, "vitality": 7, "agility": 4, "intuition": 4}
        combat_stats = {"max_hp": 120, "current_hp": 120, "attack": 12, "defense": 8, 
                       "dodge": 4, "accuracy": 88, "crit_chance": 4, "crit_damage": 150}
    elif "Маг" in chosen_class:
        base_stats = {"strength": 2, "intelligence": 8, "vitality": 5, "agility": 5, "intuition": 5}
        combat_stats = {"max_hp": 80, "current_hp": 80, "attack": 14, "defense": 3, 
                       "dodge": 5, "accuracy": 90, "crit_chance": 5, "crit_damage": 160}
    elif "Лучник" in chosen_class:
        base_stats = {"strength": 6, "intelligence": 4, "vitality": 6, "agility": 7, "intuition": 2}
        combat_stats = {"max_hp": 90, "current_hp": 90, "attack": 13, "defense": 4, 
                       "dodge": 8, "accuracy": 85, "crit_chance": 7, "crit_damage": 155}
    elif "Клерик" in chosen_class:
        base_stats = {"strength": 3, "intelligence": 7, "vitality": 6, "agility": 4, "intuition": 5}
        combat_stats = {"max_hp": 95, "current_hp": 95, "attack": 10, "defense": 5, 
                       "dodge": 4, "accuracy": 92, "crit_chance": 4, "crit_damage": 145}
    
    # Начальные навыки
    active_skills = ["Удар", "Защита", None, None]
    passive_skills = []
    
    return {
        "tg_id": user_id,
        "nickname": nickname,
        "class": chosen_class,
        "registered": True,
        "location": None,
        "level": 1,
        "exp": 0,
        "exp_to_next": 100,
        "gold": 100,
        "stat_points": 0,
        "stats": base_stats,
        "combat": combat_stats,
        "inventory": {
            "weapons": [],
            "helmets": [],
            "armors": [],
            "gloves": [],
            "boots": [],
            "rings": [],
            "amulets": []
        },
        "equipped": {
            "weapon": None,
            "helmet": None,
            "armor": None,
            "gloves": None,
            "boots": None,
            "ring_left": None,
            "ring_right": None,
            "amulet": None
        },
        "resources": {},
        "skills": {
            "active": active_skills,
            "passive": passive_skills,
            "available_active": ["Удар", "Защита"],
            "available_passive": ["Крепкое здоровье", "Меткий глаз"]
        }
    }

def calculate_combat_stats(player):
    """Пересчет боевых характеристик на основе статов и экипировки"""
    stats = player["stats"]
    base = player["combat"]
    
    if "Воин" in player["class"] or "Лучник" in player["class"]:
        attack_bonus = stats["strength"] * 2
    else:
        attack_bonus = stats["intelligence"] * 2
    
    base["attack"] = 10 + attack_bonus
    base["max_hp"] = 80 + stats["vitality"] * 10
    base["dodge"] = stats["agility"] * 1
    base["crit_chance"] = stats["agility"] * 0.5 + stats["intuition"] * 0.5
    base["accuracy"] = 85 + stats["intuition"] * 1
    
    if base["current_hp"] > base["max_hp"]:
        base["current_hp"] = base["max_hp"]

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
        await message.answer("Ты уже зарегистрирован!", reply_markup=get_main_keyboard())

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
    nickname = players[user_id]["nickname"]
    
    # Полная инициализация игрока
    players[user_id] = init_new_player(user_id, nickname, chosen_class)
    
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
    else:
        # Временная заглушка для других классов
        players[user_id]["location"] = "Деревня Новиков"
        await callback.message.answer(
            "📍 *Деревня Новиков*\n"
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

@dp.message(lambda message: message.text == "📊 Персонаж")
async def show_character(message: types.Message):
    user_id = message.from_user.id
    player = players.get(user_id)
    
    if not player or not player.get("registered"):
        await message.answer("Сначала зарегистрируйся! Используй /start")
        return
    
    class_icon = player["class"][:2]
    text = (
        f"*{class_icon} {player['nickname']}*\n"
        f"Уровень: {player['level']}\n"
        f"💰 Золото: {player['gold']}\n"
        f"📊 Опыт: {player['exp']}/{player['exp_to_next']}\n"
        f"❤️ Здоровье: {player['combat']['current_hp']}/{player['combat']['max_hp']}\n"
        f"⭐ Доступные очки прокачки: {player['stat_points']}"
    )
    
    await message.answer(text, reply_markup=get_character_menu_keyboard(), parse_mode="Markdown")

@dp.callback_query(lambda c: c.data == "char_stats")
async def show_stats(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    player = players[user_id]
    combat = player["combat"]
    stats = player["stats"]
    
    text = (
        f"*📈 ХАРАКТЕРИСТИКИ*\n\n"
        f"❤️ Здоровье: {combat['current_hp']}/{combat['max_hp']}\n"
        f"⚔️ Атака: {combat['attack']}\n"
        f"🛡️ Защита: {combat['defense']}\n"
        f"💨 Уворот: {combat['dodge']}%\n"
        f"🎯 Точность: {combat['accuracy']}%\n"
        f"💥 Крит. шанс: {combat['crit_chance']:.1f}%\n"
        f"💢 Крит. урон: {combat['crit_damage']}%\n\n"
    )
    
    if "Воин" in player["class"] or "Лучник" in player["class"]:
        text += f"💪 Сила: {stats['strength']}\n"
    else:
        text += f"📚 Интеллект: {stats['intelligence']}\n"
    
    text += (
        f"❤️ Выносливость: {stats['vitality']}\n"
        f"🏃 Ловкость: {stats['agility']}\n"
        f"🔮 Интуиция: {stats['intuition']}\n\n"
        f"⭐ Очки прокачки: {player['stat_points']}"
    )
    
    await callback.message.edit_text(
        text,
        reply_markup=get_stats_keyboard(player["class"]),
        parse_mode="Markdown"
    )
    await callback.answer()

@dp.callback_query(lambda c: c.data.startswith("stat_"))
async def stat_info(callback: types.CallbackQuery, state: FSMContext):
    stat_key = callback.data.replace("stat_", "")
    user_id = callback.from_user.id
    player = players[user_id]
    
    if player["stat_points"] <= 0:
        await callback.answer("❌ Нет доступных очков прокачки!")
        return
    
    stat_names = {
        "strength": "Сила",
        "intelligence": "Интеллект",
        "vitality": "Выносливость",
        "agility": "Ловкость",
        "intuition": "Интуиция"
    }
    
    stat_descriptions = {
        "strength": "Повышает атаку на 2 ед. за очко",
        "intelligence": "Повышает атаку на 2 ед. за очко",
        "vitality": "Повышает макс. здоровье на 10 ед. за очко",
        "agility": "Повышает уворот на 1% и шанс крита на 0.5% за очко",
        "intuition": "Повышает точность на 1% и шанс крита на 0.5% за очко"
    }
    
    await state.update_data(selected_stat=stat_key)
    await state.set_state(StatDistribution.waiting_for_amount)
    
    builder = InlineKeyboardBuilder()
    for i in [1, 2, 3, 4, 5]:
        builder.button(text=str(i), callback_data=f"amount_{i}")
    builder.button(text="◀️ Назад", callback_data="char_stats")
    builder.adjust(5)
    
    await callback.message.edit_text(
        f"*{stat_names[stat_key]}*\n\n"
        f"{stat_descriptions[stat_key]}\n\n"
        f"Доступно очков: {player['stat_points']}\n"
        f"Выбери сколько очков вложить:",
        reply_markup=builder.as_markup(),
        parse_mode="Markdown"
    )
    await callback.answer()

@dp.callback_query(lambda c: c.data.startswith("amount_"), StatDistribution.waiting_for_amount)
async def distribute_stats(callback: types.CallbackQuery, state: FSMContext):
    amount = int(callback.data.replace("amount_", ""))
    user_id = callback.from_user.id
    player = players[user_id]
    data = await state.get_data()
    stat_key = data["selected_stat"]
    
    if amount > player["stat_points"]:
        await callback.answer("❌ Недостаточно очков!")
        return
    
    player["stats"][stat_key] += amount
    player["stat_points"] -= amount
    calculate_combat_stats(player)
    
    await state.clear()
    await callback.answer(f"✅ Вложено {amount} очков!")
    await show_stats(callback)

@dp.callback_query(lambda c: c.data == "char_items")
async def show_items_menu(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "*🎒 ПРЕДМЕТЫ*\n\n"
        "Выбери категорию:",
        reply_markup=get_items_category_keyboard(),
        parse_mode="Markdown"
    )
    await callback.answer()

@dp.callback_query(lambda c: c.data.startswith("item_"))
async def show_items_category(callback: types.CallbackQuery):
    category = callback.data.replace("item_", "")
    user_id = callback.from_user.id
    player = players[user_id]
    
    category_names = {
        "weapons": "⚔️ Оружие",
        "helmets": "⛑️ Шлемы",
        "armors": "🛡️ Доспехи",
        "gloves": "🧤 Перчатки",
        "boots": "👢 Сапоги",
        "rings": "💍 Кольца",
        "amulets": "📿 Амулеты"
    }
    
    items = player["inventory"][category]
    
    if not items:
        text = f"*{category_names[category]}*\n\nУ тебя нет предметов в этой категории."
    else:
        text = f"*{category_names[category]}*\n\n"
        for i, item in enumerate(items, 1):
            text += f"{i}. {item['name']} (Ур. {item.get('level', 1)})\n"
    
    builder = InlineKeyboardBuilder()
    if items:
        for i, item in enumerate(items, 1):
            builder.button(text=str(i), callback_data=f"equip_{category}_{i-1}")
        builder.adjust(5)
    builder.row(InlineKeyboardButton(text="◀️ Назад", callback_data="char_items"))
    
    await callback.message.edit_text(text, reply_markup=builder.as_markup(), parse_mode="Markdown")
    await callback.answer()

@dp.callback_query(lambda c: c.data.startswith("equip_"))
async def equip_item(callback: types.CallbackQuery):
    parts = callback.data.split("_")
    category = parts[1]
    index = int(parts[2])
    user_id = callback.from_user.id
    player = players[user_id]
    
    item = player["inventory"][category][index]
    
    # Экипировка предмета
    if category == "weapons":
        player["equipped"]["weapon"] = item
    elif category == "helmets":
        player["equipped"]["helmet"] = item
    elif category == "armors":
        player["equipped"]["armor"] = item
    elif category == "gloves":
        player["equipped"]["gloves"] = item
    elif category == "boots":
        player["equipped"]["boots"] = item
    elif category == "rings":
        # Проверка колец
        if not player["equipped"]["ring_left"]:
            player["equipped"]["ring_left"] = item
        elif not player["equipped"]["ring_right"]:
            player["equipped"]["ring_right"] = item
        else:
            await callback.answer("❌ Оба слота колец заняты!")
            return
    elif category == "amulets":
        player["equipped"]["amulet"] = item
    
    calculate_combat_stats(player)
    await callback.answer(f"✅ {item['name']} экипирован!")
    await show_items_category(callback)

@dp.callback_query(lambda c: c.data == "char_resources")
async def show_resources(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    player = players[user_id]
    resources = player["resources"]
    
    if not resources:
        text = "*📦 РЕСУРСЫ*\n\nУ тебя пока нет ресурсов."
    else:
        text = "*📦 РЕСУРСЫ*\n\n"
        for res, amount in resources.items():
            text += f"• {res}: {amount} шт.\n"
    
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_character"))
    
    await callback.message.edit_text(text, reply_markup=builder.as_markup(), parse_mode="Markdown")
    await callback.answer()

@dp.callback_query(lambda c: c.data == "char_skills")
async def show_skills_menu(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    player = players[user_id]
    skills = player["skills"]
    
    active_text = "🎯 *АКТИВНЫЕ НАВЫКИ*\n"
    for i, skill in enumerate(skills["active"], 1):
        active_text += f"Слот {i}: {skill if skill else 'Пусто'}\n"
    
    await callback.message.edit_text(
        active_text,
        reply_markup=get_skills_menu_keyboard(),
        parse_mode="Markdown"
    )
    await callback.answer()

@dp.callback_query(lambda c: c.data.startswith("skill_change_"))
async def change_skill_slot(callback: types.CallbackQuery, state: FSMContext):
    slot = int(callback.data.replace("skill_change_", ""))
    user_id = callback.from_user.id
    player = players[user_id]
    
    available = player["skills"]["available_active"]
    
    if not available:
        await callback.answer("❌ Нет доступных навыков!")
        return
    
    await state.update_data(skill_slot=slot - 1)
    await state.set_state(SkillChange.waiting_for_skill_choice)
    
    text = f"*Выбери навык для слота {slot}:*\n\n"
    builder = InlineKeyboardBuilder()
    for i, skill in enumerate(available, 1):
        text += f"{i}. {skill}\n"
        builder.button(text=str(i), callback_data=f"choose_skill_{i-1}")
    builder.adjust(5)
    builder.row(InlineKeyboardButton(text="◀️ Назад", callback_data="char_skills"))
    
    await callback.message.edit_text(text, reply_markup=builder.as_markup(), parse_mode="Markdown")
    await callback.answer()

@dp.callback_query(lambda c: c.data.startswith("choose_skill_"), SkillChange.waiting_for_skill_choice)
async def set_skill(callback: types.CallbackQuery, state: FSMContext):
    skill_index = int(callback.data.replace("choose_skill_", ""))
    user_id = callback.from_user.id
    player = players[user_id]
    data = await state.get_data()
    slot = data["skill_slot"]
    
    chosen_skill = player["skills"]["available_active"][skill_index]
    player["skills"]["active"][slot] = chosen_skill
    
    await state.clear()
    await callback.answer(f"✅ Навык '{chosen_skill}' установлен в слот {slot + 1}!")
    await show_skills_menu(callback)

@dp.callback_query(lambda c: c.data == "skill_passive")
async def show_passive_skills(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    player = players[user_id]
    
    available = player["skills"]["available_passive"]
    active = player["skills"]["passive"]
    
    text = "*⭐ ПАССИВНЫЕ НАВЫКИ*\n\n"
    builder = InlineKeyboardBuilder()
    
    for skill in available:
        status = "✅" if skill in active else "❌"
        text += f"{status} {skill}\n"
        builder.button(
            text=f"{status} {skill}", 
            callback_data=f"toggle_passive_{skill}"
        )
    
    builder.adjust(1)
    builder.row(InlineKeyboardButton(text="◀️ Назад", callback_data="char_skills"))
    
    await callback.message.edit_text(text, reply_markup=builder.as_markup(), parse_mode="Markdown")
    await callback.answer()

@dp.callback_query(lambda c: c.data.startswith("toggle_passive_"))
async def toggle_passive(callback: types.CallbackQuery):
    skill = callback.data.replace("toggle_passive_", "")
    user_id = callback.from_user.id
    player = players[user_id]
    
    if skill in player["skills"]["passive"]:
        player["skills"]["passive"].remove(skill)
        await callback.answer(f"❌ {skill} отключен")
    else:
        player["skills"]["passive"].append(skill)
        await callback.answer(f"✅ {skill} включен")
    
    await show_passive_skills(callback)

@dp.callback_query(lambda c: c.data == "back_to_character")
async def back_to_character(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    player = players[user_id]
    
    class_icon = player["class"][:2]
    text = (
        f"*{class_icon} {player['nickname']}*\n"
        f"Уровень: {player['level']}\n"
        f"💰 Золото: {player['gold']}\n"
        f"📊 Опыт: {player['exp']}/{player['exp_to_next']}\n"
        f"❤️ Здоровье: {player['combat']['current_hp']}/{player['combat']['max_hp']}\n"
        f"⭐ Доступные очки прокачки: {player['stat_points']}"
    )
    
    await callback.message.edit_text(
        text,
        reply_markup=get_character_menu_keyboard(),
        parse_mode="Markdown"
    )
    await callback.answer()

@dp.callback_query(lambda c: c.data == "char_back")
async def char_back(callback: types.CallbackQuery):
    await callback.message.delete()
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
        "buy_hp_potion": ("🧪 Малое зелье здоровья", "+50 HP", 30),
        "buy_mana_potion": ("💙 Малое зелье маны", "+20 маны", 40),
        "buy_rage_potion": ("🔥 Зелье ярости", "+30 ярости", 30),
        "buy_energy_potion": ("⚡ Зелье энергии", "+30 энергии", 30),
        "buy_stance_potion": ("🛡️ Зелье стойки", "+30 стойки", 30)
    }
    
    item = items.get(callback.data)
    if not item:
        await callback.answer("Товар не найден")
        return
    
    user_id = callback.from_user.id
    player = players[user_id]
    
    if player["gold"] < item[2]:
        await callback.answer(f"❌ Недостаточно золота! Нужно {item[2]} золота.")
        return
    
    player["gold"] -= item[2]
    
    # Добавление зелья в ресурсы
    if "зелья" not in player["resources"]:
        player["resources"]["зелья"] = {}
    if item[0] not in player["resources"]["зелья"]:
        player["resources"]["зелья"][item[0]] = 0
    player["resources"]["зелья"][item[0]] += 1
    
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="◀️ Назад к товарам", callback_data="citizen_merchant"))
    
    await callback.message.edit_text(
        f"✅ *Покупка совершена!*\n\n"
        f"Ты приобрёл: {item[0]}\n"
        f"Эффект: {item[1]}\n"
        f"Потрачено: {item[2]} золота\n"
        f"Осталось золота: {player['gold']}",
        reply_markup=builder.as_markup(),
        parse_mode="Markdown"
    )
    await callback.answer("✅ Покупка успешна!")

@dp.callback_query(lambda c: c.data == "back_to_citizens")
async def back_to_citizens(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "👥 *ЖИТЕЛИ ЛЮМИНАРЫ*\n\n"
        "На центральной площади ты видишь несколько человек. К кому подойдёшь?",
        reply_markup=get_citizens_keyboard(),
        parse_mode="Markdown"
    )
    await callback.answer()

@dp.message(lambda message: message.text in ["🗺️ Путешествие", "🛡️ Клан", "📜 Квесты", "⚙️ Меню", "👫 Друзья", "❓ Помощь"])
async def under_development(message: types.Message):
    await message.answer("🚧 Этот раздел в разработке!")

async def main():
    print("✅ Бот запущен и готов к работе!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())