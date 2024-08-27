import aiogram
import states
import aiogram.fsm
import aiogram.fsm.context
import utils
import sqlite3

router = aiogram.Router()


@router.message(aiogram.F.text=='/admin')
async def admin(message : aiogram.types.Message):
    if message.from_user.id == 2096978507:
        await message.answer(
'''
Выдать подписку - /grand_sub
Количество пользователей открывших бота - /count_all_users
Количество пользователей с подпиской - /count_users
Изменить цену подписки - /change_cost
'''
        )
    else:
        await message.answer(
            'У вас нет доступа к админке'
        )


@router.message(aiogram.F.text=='/grand_sub')
async def grand_sub_command(message : aiogram.types.Message, state : aiogram.fsm.context.FSMContext):
    await state.set_state(states.AdminState.grand_sub)
    await message.answer(
        'Отправьте id пользователя которому нужно выдать подписку'
    )


@router.message(states.AdminState.grand_sub)
async def grand_sub(message : aiogram.types.Message, state : aiogram.fsm.context.FSMContext):
    await state.set_state(None)
    if message.from_user.id == 2096978507:
        utils.set_user_subscription(
            message.from_user.id,
            1,
            '2050-09-26T23:15:43.227305'
        )
        await message.answer('Подписка выдана')
    else:
        await message.answer('Отказано в доступе')


@router.message(aiogram.F.text == '/count_all_users')
async def count_all_users(message : aiogram.types.Message):
    if message.from_user.id == 2096978507:
        conn = sqlite3.connect('db.sqlite')
        cur = conn.cursor()
        cur.execute('SELECT id FROM users;')
        await message.answer(
            str(len(cur.fetchall()))
        )
        cur.close()
        conn.close()
    else:
        await message.answer('Отказано в доступе')


@router.message(aiogram.F.text == '/count_users')
async def count_users(message : aiogram.types.Message):
    if message.from_user.id == 2096978507:
        conn = sqlite3.connect('db.sqlite')
        cur = conn.cursor()
        cur.execute('SELECT id FROM users WHERE subscription=1;')
        await message.answer(
            str(len(cur.fetchall()))
        )
        cur.close()
        conn.close()
    else:
        await message.answer('Отказано в доступе')


@router.message(aiogram.F.text == '/change_cost')
async def set_cost(message : aiogram.types.Message, state : aiogram.fsm.context.FSMContext):
    if message.from_user.id == 2096978507:
        await state.set_state(states.AdminState.set_sub_cost)
        await message.answer(
            'Введите новую стоимость подписки'
        )
    else:
        await message.answer('Отказано в доступе')


@router.message(states.AdminState.set_sub_cost)
async def set_sub_cost(message : aiogram.types.Message, state : aiogram.fsm.context.FSMContext):
    await state.set_state(None)
    if message.from_user.id == 2096978507:
        try:
            file = open('sub_cost.txt', 'w')
            file.write(message.text)
            file.close()
        except Exception as e:
            print(e)
        await message.answer('Стоимость изменена')
    else:
        await message.answer('Отказано в доступе')
