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
        "gold": 1000,
        "stat_points": 10,
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
        "resources": {
            "potions": {}
        },
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
    
    # Добавляем бонусы от экипировки
    for slot, item in player["equipped"].items():
        if item:
            for stat, bonus in item.get("bonuses", {}).items():
                if stat in base:
                    base[stat] += bonus
    
    if base["current_hp"] > base["max_hp"]:
        base["current_hp"] = base["max_hp"]