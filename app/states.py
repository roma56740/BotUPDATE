from aiogram.fsm.state import State, StatesGroup

class RegistrationState(StatesGroup):
    choosing_role = State()
    choosing_manager_name = State()

class HelpColleagueState(StatesGroup):
    entering_description = State()
    entering_username = State()

class AdminHeartAction(StatesGroup):
    waiting_username = State()
    reason_input = State()
    penalty_amount = State()

class AdminRemoveHeartState(StatesGroup):
    waiting_username = State()
    reason_input = State()
    penalty_reason = State()
    penalty_value = State()

class AdminUsernameInput(StatesGroup):
    waiting_username = State()
