import aiogram
import aiogram.fsm
import aiogram.fsm.context
import utils
import datetime as dt
import keyboards
import states
import requests
import uuid

router = aiogram.Router()


@router.message(aiogram.F.text=='/pay')
async def invoicing(message : aiogram.types.Message, state : aiogram.fsm.context.FSMContext):
    cost = int(open('sub_cost.txt').read())
    await state.set_state(states.PayState.select_sub_type)
    await message.answer(
f'''
На какой срок желаете преобрести подписку?
1 месяц: {cost}р
3 месяца: ~{3 * cost}р~ {(3 * cost // 100) * 85}
6 месяцев: ~{6 * cost}р~ {(6 * cost // 100) * 70}
''',
        parse_mode='MarkdownV2',
        reply_markup=keyboards.select_sub_keyboard
    )


@router.callback_query(states.PayState.select_sub_type)
async def get_sub_type(callback : aiogram.types.CallbackQuery, state : aiogram.fsm.context.FSMContext):
    await callback.answer()
    await callback.message.edit_reply_markup(reply_markup=None)
    await state.set_state(states.PayState.get_email)
    await state.set_data({'sub': callback.data})
    await callback.message.answer(
        'Введите вашу почту, на нее отправим чек'
    )


@router.message(states.PayState.get_email)
async def get_email(message : aiogram.types.Message, state : aiogram.fsm.context.FSMContext):
    month_cost = int(open('sub_cost.txt').read())
    cost = open('sub_cost.txt').read()
    sub = (await state.get_data())['sub']
    if sub == '1':
        description = 'Подписка на 1 месяц'
        cost = month_cost
    elif sub == '3':
        description = 'Подписка на 3 месяца'
        cost = month_cost * 3 // 100 * 85
    elif sub == '6':
        description = 'Подписка на 6 месяцев'
        cost = month_cost * 6 // 100 * 70
    await state.set_state(None)
    req = requests.post(
        'https://api.yookassa.ru/v3/payments',
        headers={
            'Content-Type': 'application/json',
            'Idempotence-Key': str(uuid.uuid4())
        },
        json={
            'amount': {
                'value': f'{cost}.00',
                'currency': 'RUB'
            },
            'capture': True,
            'confirmation': {
                'type': 'redirect',
                'return_url': 'https://t.me/AVPNmanagerBot'
            },
            'description': description,
            'receipt': {
                'customer': {
                    'email': message.text
                },
                'items': [
                    {
                        'description': description,
                        'quantity': 1,
                        'amount': {
                            'value': f'{cost}.00',
                            'currency': 'RUB'
                        },
                        'vat_code': 1
                    }
                ]
            }
        },
        auth=('441601', 'live_hNO32idIQ5jcuFy02G3VUAtbt4RXJfK9rySVW5tDh9k')
    )
    data = req.json()
    await state.set_data({'id': data['id'], 'sub': sub})
    await state.set_state(states.PayState.get_sub)
    url = data['confirmation']['confirmation_url']
    await message.answer(
        f'<a href="{url}">Оплатите подписку</a>',
        reply_markup=keyboards.get_pay_keyboard,
        parse_mode='html'
    )


@router.callback_query(states.PayState.get_sub)
async def get_payment(callback : aiogram.types.CallbackQuery, state : aiogram.fsm.context.FSMContext):
    await callback.answer()
    if callback.data == '2':
        await state.set_state(None)
        await callback.message.delete()
        return
    data = await state.get_data()
    id = data['id']
    sub = int(data['sub'])
    req = requests.get(
        f'https://api.yookassa.ru/v3/payments/{id}',
        auth=('441601', 'live_hNO32idIQ5jcuFy02G3VUAtbt4RXJfK9rySVW5tDh9k')
    )
    data = req.json()
    if data['status'] != 'succeeded':
        await callback.message.answer('Вы еще не оплатили подписку')
    else:
        utils.set_user_subscription(
            callback.from_user.id,
            1,
            (dt.datetime.now() + dt.timedelta(days=30 * sub)).isoformat()
        )
        await callback.message.edit_reply_markup(reply_markup=None)
        await callback.message.answer(
            'Оплата произведена успешно!\nИнструкция по подключению VPN - /instruction\nУправление устройствами - /management'
        )
