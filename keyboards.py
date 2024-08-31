import aiogram.utils
import aiogram.utils.keyboard
import utils
import aiogram


def make_choose_device_keyboard(user_id):
    keyboard = []
    devices = utils.get_user_devices(user_id)
    if not devices:
        return False
    for device in devices:
        keyboard.append([
            aiogram.types.InlineKeyboardButton(
                text=device[0] + ' ' + ('🟢' if device[1] else '🔴'),
                callback_data=f'{device[0]};;;{device[1]};;;{device[2]}'
            )
        ]
        )
    return aiogram.types.InlineKeyboardMarkup(
        inline_keyboard=keyboard
    )


def make_manage_device_keyboard(data):
    data = data.split(';;;')
    device_id = int(data[2])
    is_work = bool(int(data[1]))
    keyboard = [
        [
            aiogram.types.InlineKeyboardButton(
                text='Удалить',
                callback_data=f'del {device_id}'
            )
        ],
        [
            aiogram.types.InlineKeyboardButton(
                text='Файл/QR для подключения',
                callback_data=f'file {device_id}'
            )   
        ],
        []
    ]
    if is_work:
        keyboard[-1].append(
            aiogram.types.InlineKeyboardButton(
                text='Отклюить',
                callback_data=f'off {device_id}'
            )
        )
    else:
        keyboard[-1].append(
            aiogram.types.InlineKeyboardButton(
                text='Вклюить',
                callback_data=f'on {device_id}'
            )
        )
    return aiogram.types.InlineKeyboardMarkup(
        inline_keyboard=keyboard
    )


select_sub_keyboard = aiogram.types.InlineKeyboardMarkup(
    inline_keyboard=[
        [aiogram.types.InlineKeyboardButton(text='1 месяц', callback_data='1')],
        [aiogram.types.InlineKeyboardButton(text='3 месяца', callback_data='3')],
        [aiogram.types.InlineKeyboardButton(text='6 месяцев', callback_data='6')]
    ]
)

select_sub_keyboard_with_free = aiogram.types.InlineKeyboardMarkup(
    inline_keyboard=[
        [aiogram.types.InlineKeyboardButton(text='1 неделя', callback_data='0')],
        [aiogram.types.InlineKeyboardButton(text='1 месяц', callback_data='1')],
        [aiogram.types.InlineKeyboardButton(text='3 месяца', callback_data='3')],
        [aiogram.types.InlineKeyboardButton(text='6 месяцев', callback_data='6')]
    ]
)

get_pay_keyboard = aiogram.types.InlineKeyboardMarkup(
    inline_keyboard=[
        [aiogram.types.InlineKeyboardButton(text='Я оплатил', callback_data='1')],
        [aiogram.types.InlineKeyboardButton(text='Передумал оплачивать', callback_data='2')]
    ]
)
