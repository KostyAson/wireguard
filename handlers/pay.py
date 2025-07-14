import aiogram
import aiogram.fsm
import aiogram.fsm.context
import utils
import datetime as dt
import states
import requests
import uuid
import os
import dotenv
import log
import asyncio

router = aiogram.Router()

dotenv.load_dotenv('.env')


@router.message(aiogram.F.text=='/pay')
async def invoicing(message : aiogram.types.Message, state : aiogram.fsm.context.FSMContext):
    log.logger.info(f"Пользователь {utils.get_user_username(message)} отправил комманду pay")
    if not utils.check_user_sub(message.from_user.id):
        cost = int(open('sub_cost.txt').read())
        await state.set_state(states.PayState.get_email)
        await message.answer(
            f'Стоимость подписки на 1 месяц: {cost}р\n\nНапишите вашу почту, на неё отправим чек после оплаты 🖊',
            parse_mode='MarkdownV2'
        )
    else:
        await message.answer(f'У вас уже есть действующая подписка до:\n{utils.get_user_subdate(message.from_user.id)}')


@router.message(states.PayState.get_email)
async def get_email(message : aiogram.types.Message, state : aiogram.fsm.context.FSMContext, bot : aiogram.Bot):
    description = 'Подписка на 1 месяц'
    cost = int(open('sub_cost.txt').read())
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
    id = data['id']
    url = data['confirmation']['confirmation_url']
    await message.answer(
        f'<a href="{url}">Оплатите подписку</a>\n\nСсылка действительна в течении 5 минут',
        parse_mode='html'
    )
    for _ in range(7):
        await asyncio.sleep(45)
        req = requests.get(
            f'https://api.yookassa.ru/v3/payments/{id}',
            auth=('441601', os.getenv('youkassa'))
        )
        data = req.json()
        if data['status'] == 'succeeded':
            utils.set_user_subscription(
                message.from_user.id,
                1,
                (dt.datetime.now() + dt.timedelta(days=30)).isoformat()
            )
            utils.update_server_config()
            await bot.send_message(2096978507, f'Пользователь @{utils.get_user_username(message)} оплатил подписку')
            await message.edit_reply_markup(reply_markup=None)
            await message.answer(
                'Оплата произведена успешно, VPN снова работает, спасибо за доверие! ✅'
            )
            log.logger.info(f"Пользователь {utils.get_user_username(message)} оплатил подписку на 1 месяц")
            user_ref = utils.get_user_ref(message.from_user.id)
            if user_ref is not None:
                name = utils.get_user_username(message)
                sub_ref = utils.grand_ref_sub(user_ref)
                if sub_ref:
                    await bot.send_message(chat_id=user_ref, text=f'Пользователь {name} перешел по вашей ссылке и оплатил подписку. Продлили вашу подписку на 1 неделю')
                else:
                    await bot.send_message(chat_id=user_ref, text=f'Пользователь {name} перешел по вашей ссылке и оплатил подписку. Выдали вам подписку на 1 неделю')
            break
    else:
        await message.answer('Срок действия ссылки истёк\n\nДля повторной оплаты отправьте команду /pay')
    await state.set_state(None)
