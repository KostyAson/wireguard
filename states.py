import aiogram.fsm.state


class AddDevice(aiogram.fsm.state.StatesGroup):
    get_name = aiogram.fsm.state.State()


class ManageDevice(aiogram.fsm.state.StatesGroup):
    choose_device = aiogram.fsm.state.State()
    get_manage_type = aiogram.fsm.state.State()


class AdminState(aiogram.fsm.state.StatesGroup):
    grand_sub = aiogram.fsm.state.State()
    set_sub_cost = aiogram.fsm.state.State()
    send_message = aiogram.fsm.state.State()
    add_ip = aiogram.fsm.state.State()
    send_to_user = aiogram.fsm.state.State()
    del_add = aiogram.fsm.state.State()


class AddAdState(aiogram.fsm.state.StatesGroup):
    get_title = aiogram.fsm.state.State()
    get_description = aiogram.fsm.state.State()
    get_limit = aiogram.fsm.state.State()
    get_free_time = aiogram.fsm.state.State()
    get_message = aiogram.fsm.state.State()


class PayState(aiogram.fsm.state.StatesGroup):
    select_sub_type = aiogram.fsm.state.State()
    get_email = aiogram.fsm.state.State()
    get_sub = aiogram.fsm.state.State()
