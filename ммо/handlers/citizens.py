from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder
from config import players
from keyboards import get_main_keyboard, get_citizens_keyboard, get_merchant_keyboard

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

async def back_to_city(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "📍 *Люминара — Центральная площадь*\n"
        "Куда направишься, путник?",
        parse_mode="Markdown"
    )
    await callback.answer()

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

async def show_item_info(callback: types.CallbackQuery):
    """Показывает информацию о товаре перед покупкой"""
    items = {
        "buy_hp_potion": {
            "name": "🧪 Малое зелье здоровья",
            "desc": "Восстанавливает 50 единиц здоровья. Имеет приятный травяной вкус.",
            "effect": "❤️ +50 HP",
            "price": 30
        },
        "buy_mana_potion": {
            "name": "💙 Малое зелье маны",
            "desc": "Восстанавливает 20 единиц маны. Светится голубым сиянием.",
            "effect": "💙 +20 маны",
            "price": 40
        },
        "buy_rage_potion": {
            "name": "🔥 Зелье ярости",
            "desc": "Восстанавливает 30 единиц ярости. При употреблении чувствуется прилив сил.",
            "effect": "🔥 +30 ярости",
            "price": 30
        },
        "buy_energy_potion": {
            "name": "⚡ Зелье энергии",
            "desc": "Восстанавливает 30 единиц энергии. Искрит в руках.",
            "effect": "⚡ +30 энергии",
            "price": 30
        },
        "buy_stance_potion": {
            "name": "🛡️ Зелье стойки",
            "desc": "Восстанавливает 30 единиц стойки. Укрепляет дух и тело.",
            "effect": "🛡️ +30 стойки",
            "price": 30
        }
    }
    
    item = items.get(callback.data)
    if not item:
        await callback.answer("Товар не найден")
        return
    
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="✅ Купить", callback_data=f"confirm_buy_{callback.data}"))
    builder.row(InlineKeyboardButton(text="◀️ Назад к товарам", callback_data="citizen_merchant"))
    
    await callback.message.edit_text(
        f"*{item['name']}*\n\n"
        f"📜 *Описание:* {item['desc']}\n"
        f"✨ *Эффект:* {item['effect']}\n"
        f"💰 *Цена:* {item['price']} золота\n\n"
        f"Желаешь приобрести?",
        reply_markup=builder.as_markup(),
        parse_mode="Markdown"
    )
    await callback.answer()

async def confirm_buy_item(callback: types.CallbackQuery):
    """Подтверждение и выполнение покупки"""
    item_key = callback.data.replace("confirm_buy_", "")
    
    items = {
        "buy_hp_potion": ("🧪 Малое зелье здоровья", "+50 HP", 30),
        "buy_mana_potion": ("💙 Малое зелье маны", "+20 маны", 40),
        "buy_rage_potion": ("🔥 Зелье ярости", "+30 ярости", 30),
        "buy_energy_potion": ("⚡ Зелье энергии", "+30 энергии", 30),
        "buy_stance_potion": ("🛡️ Зелье стойки", "+30 стойки", 30)
    }
    
    item = items.get(item_key)
    if not item:
        await callback.answer("Товар не найден")
        return
    
    user_id = callback.from_user.id
    player = players[user_id]
    
    if player["gold"] < item[2]:
        await callback.answer(f"❌ Недостаточно золота! Нужно {item[2]} золота.")
        return
    
    player["gold"] -= item[2]
    
    if "potions" not in player["resources"]:
        player["resources"]["potions"] = {}
    if item[0] not in player["resources"]["potions"]:
        player["resources"]["potions"][item[0]] = 0
    player["resources"]["potions"][item[0]] += 1
    
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="◀️ Назад к товарам", callback_data="citizen_merchant"))
    builder.row(InlineKeyboardButton(text="🏺 К торговцу", callback_data="citizen_merchant"))
    
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

async def back_to_citizens(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "👥 *ЖИТЕЛИ ЛЮМИНАРЫ*\n\n"
        "На центральной площади ты видишь несколько человек. К кому подойдёшь?",
        reply_markup=get_citizens_keyboard(),
        parse_mode="Markdown"
    )
    await callback.answer()