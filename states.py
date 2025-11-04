from aiogram.fsm.state import StatesGroup, State


class SignupStates(StatesGroup):
    name = State()
    age = State()
    phone = State()
    role = State()
    certificate = State()
    check = State()
