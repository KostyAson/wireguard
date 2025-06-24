import aiogram
import aiogram.fsm
import aiogram.fsm.context
import keyboards
import utils
import states
import os
import log

router = aiogram.Router()


@router.message(aiogram.F.text=='/add')
async def add_device(message : aiogram.types.Message, state : aiogram.fsm.context.FSMContext):
    log.logger.info(f"Пользователь {utils.get_user_username(message)} отправил комманду add")
    if utils.check_user_sub(message.from_user.id):
        if len(utils.get_user_devices(message.from_user.id)) < 3 or message.from_user.id == 2096978507 or (message.from_user.id in (802024759, 792248687) and len(utils.get_user_devices(message.from_user.id)) <= 4):
            await state.set_state(states.AddDevice.get_name)
            await message.answer('Отправьте название для нового устройства 🖊')
        else:
            await message.answer('Вы достигли лимита в 3 устройства ❌\n\nДля добавления нового устройства, вы можете удалить одно из созданных - /management 🗑')
    else:
        await message.answer('Сначала оплатите подписку - /pay')


@router.message(states.AddDevice.get_name)
async def get_device_name(message : aiogram.types.Message, state : aiogram.fsm.context.FSMContext):
    log.logger.info(f"Пользователь {utils.get_user_username(message)} добавил новое устройство")
    await state.set_state(None)
    name = message.from_user.username
    if name is None:
        name = str(message.from_user.first_name) + " " + str(message.from_user.last_name)
    utils.add_device(message.from_user.id, message.text, name)
    normal_name = utils.get_normal_device_name(message.text)
    os.system(f'qrencode -t png -s 10 -m 1 -o qr.png < {normal_name}.conf')
    await message.answer_document(
        aiogram.types.input_file.FSInputFile(f'{normal_name}.conf'),
        caption=f'Файл для подключения к VPN с {message.text}\nИспользуйте данный файл только для одного устройства'
    )
    await message.answer_photo(
        photo=aiogram.types.FSInputFile(f'qr.png'),
        caption=f'QR для подключения к VPN с {message.text}\nИспользуйте данный QR только для одного устройства'
    )
    os.system(f'rm "{normal_name}.conf" && rm "qr.png"')


@router.message(aiogram.F.text=='/management')
async def device_management(message : aiogram.types.Message, state : aiogram.fsm.context.FSMContext):
    log.logger.info(f"Пользователь {utils.get_user_username(message)} отправил комманду management")
    if utils.check_user_sub(message.from_user.id):
        keyboard = keyboards.make_choose_device_keyboard(message.from_user.id)
        if not keyboard:
            await message.answer(
                text='У вас нет добавленных устройств\nДобавьте командой - /add'
            )
        else:
            await state.set_state(states.ManageDevice.choose_device)
            await message.answer(
                text='Выберите устройство',
                reply_markup=keyboard
            )
    else:
        await message.answer('Сначала оплатите подписку - /pay')


@router.callback_query(states.ManageDevice.choose_device)
async def choose_device(callback : aiogram.types.CallbackQuery, state : aiogram.fsm.context.FSMContext):
    await callback.message.edit_reply_markup(
        reply_markup=None
    )
    await state.set_state(states.ManageDevice.get_manage_type)
    keyboard = keyboards.make_manage_device_keyboard(callback.data)
    await callback.answer()
    await callback.message.answer(
        text=callback.data.split(';;;')[0],
        reply_markup=keyboard
    )


@router.callback_query(states.ManageDevice.get_manage_type)
async def manage_device(callback : aiogram.types.CallbackQuery, state : aiogram.fsm.context.FSMContext):
    await callback.message.edit_reply_markup(
        reply_markup=None
    )
    await state.set_state(None)
    data = callback.data.split()
    manage_type = data[0]
    device_id = data[1]
    if manage_type == 'del':
        log.logger.info(f"Пользователь {utils.get_user_username(callback)} удалил устройство")
        utils.delete_device(device_id)
        await callback.message.answer(
            text='Устройство удалено 🗑'
        )
    elif manage_type == 'off':
        log.logger.info(f"Пользователь {utils.get_user_username(callback)} отключил устройство")
        utils.change_work_device(device_id, 0)
        await callback.message.answer(
            text='Устройство выключено 🔴'
        )
    elif manage_type == 'on':
        log.logger.info(f"Пользователь {utils.get_user_username(callback)} включил устройство")
        utils.change_work_device(device_id, 1)
        await callback.message.answer(
            text='Устройство включено  🟢'
        )
    elif manage_type == 'file':
        log.logger.info(f"Пользователь {utils.get_user_username(callback)} получил данные для подключения устройства")
        name = utils.get_device_file(device_id)
        normal_name = utils.get_normal_device_name(name)
        await callback.message.answer_document(
            aiogram.types.input_file.FSInputFile(f'{normal_name}.conf'),
            caption=f'Файл для подключения к VPN с {name}\nИспользуйте данный файл только для одного устройства'
        )
        os.system(f'qrencode -t png -s 10 -m 1 -o qr.png < {normal_name}.conf')
        await callback.message.answer_photo(
            photo=aiogram.types.FSInputFile(f'qr.png'),
            caption=f'QR для подключения к VPN с {name}\nИспользуйте данный QR только для одного устройства'
        )
        os.system(f'rm "{normal_name}.conf" && rm qr.png')
