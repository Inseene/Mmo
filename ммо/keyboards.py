from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

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
        InlineKeyboardButton(text="🧪 Малое зелье здоровья (30💰)", callback_data="buy_hp_potion")
    )
    builder.row(
        InlineKeyboardButton(text="💙 Малое зелье маны (40💰)", callback_data="buy_mana_potion")
    )
    builder.row(
        InlineKeyboardButton(text="🔥 Зелье ярости (30💰)", callback_data="buy_rage_potion")
    )
    builder.row(
        InlineKeyboardButton(text="⚡ Зелье энергии (30💰)", callback_data="buy_energy_potion")
    )
    builder.row(
        InlineKeyboardButton(text="🛡️ Зелье стойки (30💰)", callback_data="buy_stance_potion")
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
        InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_character")
    )
    return builder.as_markup()

def get_distribute_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="1️⃣", callback_data="amount_1"),
        InlineKeyboardButton(text="2️⃣", callback_data="amount_2"),
        InlineKeyboardButton(text="3️⃣", callback_data="amount_3")
    )
    builder.row(
        InlineKeyboardButton(text="4️⃣", callback_data="amount_4"),
        InlineKeyboardButton(text="5️⃣", callback_data="amount_5"),
        InlineKeyboardButton(text="🔟", callback_data="amount_10")
    )
    builder.row(
        InlineKeyboardButton(text="✅ Подтвердить", callback_data="confirm_distribute"),
        InlineKeyboardButton(text="◀️ Назад", callback_data="char_stats")
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

def get_resources_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🧪 Зелья", callback_data="resource_potions")
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