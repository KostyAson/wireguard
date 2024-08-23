import aiogram
import aiogram.filters
import aiogram.fsm
import aiogram.fsm.context
import aiogram.fsm.state
import keyboards
import utils
import states
import os

router = aiogram.Router()


@router.message(aiogram.F.text=='/add')
async def add_device(message : aiogram.types.Message, state : aiogram.fsm.context.FSMContext):
    if utils.check_user_sub(message.from_user.id):
        await state.set_state(states.AddDevice.get_name)
        await message.answer('Отправьте название для нового устройства')
    else:
        await message.answer('Сначала оплатите подписку - /pay')


@router.message(states.AddDevice.get_name)
async def get_device_name(message : aiogram.types.Message, state : aiogram.fsm.context.FSMContext):
    await state.set_state(None)
    utils.add_device(message.from_user.id, message.text)
    await message.answer_document(
        aiogram.types.input_file.FSInputFile(f'{message.text.replace(" ", "-")}.conf'),
        caption=f'Файл для подключения к VPN с {message.text}\nИспользуйте данный файл только для одного устройства'
    )
    os.system(f'rm "{message.text.replace(" ", "-")}.conf"')


@router.message(aiogram.F.text=='/management')
async def device_management(message : aiogram.types.Message, state : aiogram.fsm.context.FSMContext):
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
        utils.delete_device(device_id)
        await callback.message.answer(
            text='Устройство удалено'
        )
    elif manage_type == 'off':
        utils.change_work_device(device_id, 0)
        await callback.message.answer(
            text='Устройство выключено'
        )
    elif manage_type == 'on':
        utils.change_work_device(device_id, 1)
        await callback.message.answer(
            text='Устройство включено'
        )
    elif manage_type == 'file':
        name = utils.get_device_file(device_id)
        await callback.message.answer_document(
            aiogram.types.input_file.FSInputFile(f'{name}.conf'),
            caption=f'Файл для подключения к VPN с {name}\nИспользуйте данный файл только для одного устройства'
        )
        os.system(f'rm "{name}.conf"')
