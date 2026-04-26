from aiogram import types
from config import players, SECRET_CODES

async def handle_secret_codes(message: types.Message):
    user_id = message.from_user.id
    code = message.text[1:]  # Убираем "/"
    
    if code in SECRET_CODES:
        player = players.get(user_id)
        if not player or not player.get("registered"):
            await message.answer("Сначала зарегистрируйся! Используй /start")
            return
        
        admin_items = {
            "weapons": [{
                "name": "⚔️ Меч администратора",
                "level": 99,
                "bonuses": {"attack": 1}
            }],
            "helmets": [{
                "name": "⛑️ Шлем администратора",
                "level": 99,
                "bonuses": {"defense": 1}
            }],
            "armors": [{
                "name": "🛡️ Доспех администратора",
                "level": 99,
                "bonuses": {"max_hp": 1}
            }],
            "gloves": [{
                "name": "🧤 Перчатки администратора",
                "level": 99,
                "bonuses": {"accuracy": 1}
            }],
            "boots": [{
                "name": "👢 Сапоги администратора",
                "level": 99,
                "bonuses": {"dodge": 1}
            }],
            "rings": [{
                "name": "💍 Кольцо администратора",
                "level": 99,
                "bonuses": {"crit_chance": 1}
            }],
            "amulets": [{
                "name": "📿 Амулет администратора",
                "level": 99,
                "bonuses": {"crit_damage": 1}
            }]
        }
        
        for category, items in admin_items.items():
            player["inventory"][category].extend(items)
        
        await message.answer(
            "🎁 *ПРОМОКОД АКТИВИРОВАН!*\n\n"
            "Ты получил сет администратора:\n"
            "⚔️ Меч администратора\n"
            "⛑️ Шлем администратора\n"
            "🛡️ Доспех администратора\n"
            "🧤 Перчатки администратора\n"
            "👢 Сапоги администратора\n"
            "💍 Кольцо администратора\n"
            "📿 Амулет администратора\n\n"
            "Эти предметы добавлены в твой инвентарь!",
            parse_mode="Markdown"
        )
    else:
        await message.answer("Неизвестная команда.")

async def under_development(message: types.Message):
    await message.answer("🚧 Этот раздел в разработке!")