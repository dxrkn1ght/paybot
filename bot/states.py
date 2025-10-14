from aiogram.fsm.state import StatesGroup, State

class BuyStates(StatesGroup):
    waiting_nick = State()
    selecting_product = State()
    entering_amount = State()
    waiting_screenshot = State()

class TopUpStates(StatesGroup):
    entering_amount = State()
    waiting_screenshot = State()
