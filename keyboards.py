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
                text='Файл для подключения',
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
