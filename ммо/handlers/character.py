from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from config import players
from states import StatDistribution, SkillChange
from keyboards import (
    get_character_menu_keyboard, get_stats_keyboard, get_distribute_keyboard,
    get_items_category_keyboard, get_resources_keyboard, get_skills_menu_keyboard
)
from player_data import calculate_combat_stats

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

async def stat_selected(callback: types.CallbackQuery, state: FSMContext):
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
    
    await state.update_data(selected_stat=stat_key, temp_amount=0)
    
    text = (
        f"*{stat_names[stat_key]}*\n\n"
        f"{stat_descriptions[stat_key]}\n\n"
        f"Текущее значение: {player['stats'][stat_key]}\n"
        f"Доступно очков: {player['stat_points']}\n"
        f"Выбрано для распределения: 0\n\n"
        f"Выбери сколько очков вложить:"
    )
    
    await callback.message.edit_text(
        text,
        reply_markup=get_distribute_keyboard(),
        parse_mode="Markdown"
    )
    await callback.answer()

async def select_amount(callback: types.CallbackQuery, state: FSMContext):
    amount = int(callback.data.replace("amount_", ""))
    user_id = callback.from_user.id
    player = players[user_id]
    data = await state.get_data()
    stat_key = data["selected_stat"]
    current_amount = data.get("temp_amount", 0)
    
    new_amount = current_amount + amount
    
    if new_amount > player["stat_points"]:
        await callback.answer(f"❌ Нельзя выбрать больше {player['stat_points']} очков!")
        return
    
    await state.update_data(temp_amount=new_amount)
    
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
    
    text = (
        f"*{stat_names[stat_key]}*\n\n"
        f"{stat_descriptions[stat_key]}\n\n"
        f"Текущее значение: {player['stats'][stat_key]}\n"
        f"Доступно очков: {player['stat_points']}\n"
        f"Выбрано для распределения: {new_amount}\n\n"
        f"Выбери сколько очков вложить или подтверди:"
    )
    
    await callback.message.edit_text(
        text,
        reply_markup=get_distribute_keyboard(),
        parse_mode="Markdown"
    )
    await callback.answer(f"➕ Добавлено {amount} очков")

async def confirm_distribute(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    player = players[user_id]
    data = await state.get_data()
    stat_key = data["selected_stat"]
    amount = data.get("temp_amount", 0)
    
    if amount <= 0:
        await callback.answer("❌ Выбери количество очков!")
        return
    
    player["stats"][stat_key] += amount
    player["stat_points"] -= amount
    calculate_combat_stats(player)
    
    await state.clear()
    await callback.answer(f"✅ Вложено {amount} очков в {stat_key}!")
    await show_stats(callback)

async def show_items_menu(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "*🎒 ПРЕДМЕТЫ*\n\n"
        "Выбери категорию:",
        reply_markup=get_items_category_keyboard(),
        parse_mode="Markdown"
    )
    await callback.answer()

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
            equipped_mark = ""
            if category == "weapons" and player["equipped"]["weapon"] == item:
                equipped_mark = " ✅"
            elif category == "helmets" and player["equipped"]["helmet"] == item:
                equipped_mark = " ✅"
            elif category == "armors" and player["equipped"]["armor"] == item:
                equipped_mark = " ✅"
            elif category == "gloves" and player["equipped"]["gloves"] == item:
                equipped_mark = " ✅"
            elif category == "boots" and player["equipped"]["boots"] == item:
                equipped_mark = " ✅"
            elif category == "rings" and (player["equipped"]["ring_left"] == item or player["equipped"]["ring_right"] == item):
                equipped_mark = " ✅"
            elif category == "amulets" and player["equipped"]["amulet"] == item:
                equipped_mark = " ✅"
                
            text += f"{i}. {item['name']} (Ур. {item.get('level', 1)}){equipped_mark}\n"
    
    builder = InlineKeyboardBuilder()
    if items:
        for i, item in enumerate(items, 1):
            builder.button(text=str(i), callback_data=f"equip_{category}_{i-1}")
        builder.adjust(5)
    builder.row(InlineKeyboardButton(text="◀️ Назад", callback_data="char_items"))
    
    await callback.message.edit_text(text, reply_markup=builder.as_markup(), parse_mode="Markdown")
    await callback.answer()

async def equip_item(callback: types.CallbackQuery):
    parts = callback.data.split("_")
    category = parts[1]
    index = int(parts[2])
    user_id = callback.from_user.id
    player = players[user_id]
    
    item = player["inventory"][category][index]
    
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

async def show_resources(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "*📦 РЕСУРСЫ*\n\n"
        "Выбери категорию ресурсов:",
        reply_markup=get_resources_keyboard(),
        parse_mode="Markdown"
    )
    await callback.answer()

async def show_potions(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    player = players[user_id]
    potions = player["resources"].get("potions", {})
    
    builder = InlineKeyboardBuilder()
    
    if not potions:
        text = "*🧪 ЗЕЛЬЯ*\n\nУ тебя пока нет зелий."
    else:
        text = "*🧪 ЗЕЛЬЯ*\n\n"
        for potion, amount in potions.items():
            text += f"{potion}: {amount} шт.\n"
            builder.row(InlineKeyboardButton(text=f"🧪 {potion} ({amount} шт.)", callback_data=f"use_potion_{potion}"))
    
    builder.row(InlineKeyboardButton(text="◀️ Назад", callback_data="char_resources"))
    await callback.message.edit_text(text, reply_markup=builder.as_markup(), parse_mode="Markdown")
    await callback.answer()

async def use_potion(callback: types.CallbackQuery):
    await callback.answer("🚧 Использование зелий в разработке!")

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

async def char_back(callback: types.CallbackQuery):
    await callback.message.delete()
    await callback.answer()