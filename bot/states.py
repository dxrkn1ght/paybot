from aiogram.fsm.state import StatesGroup, State
class SetupStates(StatesGroup):
    asking_nick = State()
class BuyStates(StatesGroup):
    choosing_coin_amount = State()
    confirming_purchase = State()
class TopUpStates(StatesGroup):
    entering_amount = State()
    waiting_screenshot = State()
