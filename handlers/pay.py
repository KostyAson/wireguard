import aiogram
import aiogram.fsm
import aiogram.fsm.context
import utils
import datetime as dt
import keyboards
import states
import requests
import uuid
import os
import dotenv
import log

router = aiogram.Router()

dotenv.load_dotenv('.env')


@router.message(aiogram.F.text=='/pay')
async def invoicing(message : aiogram.types.Message, state : aiogram.fsm.context.FSMContext):
    log.logger.info(f"Пользователь {utils.get_user_username(message)} отправил комманду pay")
    if not utils.check_user_sub(message.from_user.id):
        cost = int(open('sub_cost.txt').read())
        await state.set_state(states.PayState.select_sub_type)
        ans = f'''
1 месяц: {cost}р'''
        keyboard = keyboards.select_sub_keyboard
        if utils.get_user_use_free_sub(message.from_user.id):
            ans = '1 неделя: бесплтано' + ans
            keyboard = keyboards.select_sub_keyboard_with_free
        ans = 'На какой срок желаете преобрести подписку?\n' + ans
        await message.answer(
            ans,
            parse_mode='MarkdownV2',
            reply_markup=keyboard
        )
    else:
        await message.answer(f'У вас уже есть действующая подписка до:\n{utils.get_user_subdate(message.from_user.id)}')


@router.callback_query(states.PayState.select_sub_type)
async def get_sub_type(callback : aiogram.types.CallbackQuery, state : aiogram.fsm.context.FSMContext):
    await callback.answer()
    await callback.message.edit_reply_markup(reply_markup=None)
    if callback.data == '0':
        log.logger.info(f"Пользователь {utils.get_user_username(callback)} взял пробную подписку")
        await callback.message.answer('Подписка на неделю оформлена ✅\n\nИнструкция по подключению VPN - /instruction 📄\nУправление устройствами - /management ⚙')
        utils.set_user_use_free_sub(callback.from_user.id)
        utils.set_user_subscription(
            callback.from_user.id,
            1,
            (dt.datetime.now() + dt.timedelta(days=7)).isoformat()
        )
        return
    await state.set_state(states.PayState.get_email)
    await state.set_data({'sub': callback.data})
    await callback.message.answer(
        'Введите вашу почту, на нее отправим чек 🖊'
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
        cost = month_cost * 6 // 100 * 80
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
        auth=('441601', os.getenv('youkassa'))
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
async def get_payment(callback : aiogram.types.CallbackQuery, state : aiogram.fsm.context.FSMContext, bot :aiogram.Bot):
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
        auth=('441601', os.getenv('youkassa'))
    )
    data = req.json()
    if data['status'] != 'succeeded':
        await callback.message.answer('Вы еще не оплатили подписку ❌')
    else:
        utils.set_user_subscription(
            callback.from_user.id,
            1,
            (dt.datetime.now() + dt.timedelta(days=30 * sub)).isoformat()
        )
        utils.update_server_config()
        if callback.from_user.username is not None:
            await bot.send_message(2096978507, f'Пользователь @{callback.from_user.username} оплатил подписку на {sub}')
        await callback.message.edit_reply_markup(reply_markup=None)
        await callback.message.answer(
            'Оплата произведена успешно! ✅\n\nИнструкция по подключению VPN - /instruction 📄\n\nУправление устройствами - /management ⚙'
        )
        user_ref = utils.get_user_ref(callback.from_user.id)
        if user_ref is not None:
            name = callback.from_user.username
            if name is None:
                name = callback.from_user.first_name + " " + callback.from_user.last_name
            else:
                name = '@' + name
            sub_ref = utils.grand_ref_sub(user_ref, sub)
            if sub == 1:
                s = '1 неделю'
            elif sub == 3:
                s = '3 недели'
            else:
                s = '6 недель'
            log.logger.info(f"Пользователь {utils.get_user_username(callback)} оплатил подписку на {s}")
            if sub_ref:
                await bot.send_message(chat_id=user_ref, text=f'Пользователь {name} перешел по вашей ссылке и оплатил подписку. Продлили вашу подписку на {s}')
            else:
                await bot.send_message(chat_id=user_ref, text=f'Пользователь {name} перешел по вашей ссылке и оплатил подписку. Выдали вам подписку на {s}')
