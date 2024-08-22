import aiogram.fsm.state


class AddDevice(aiogram.fsm.state.StatesGroup):
    get_name = aiogram.fsm.state.State()


class ManageDevice(aiogram.fsm.state.StatesGroup):
    choose_device = aiogram.fsm.state.State()
    get_manage_type = aiogram.fsm.state.State()
