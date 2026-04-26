from aiogram.fsm.state import State, StatesGroup

class Registration(StatesGroup):
    waiting_for_nickname = State()

class StatDistribution(StatesGroup):
    waiting_for_stat = State()
    waiting_for_amount = State()

class SkillChange(StatesGroup):
    waiting_for_skill_slot = State()
    waiting_for_skill_choice = State()