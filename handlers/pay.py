import aiogram
import aiogram.fsm
import aiogram.fsm.context
import utils
import json
import datetime as dt
import keyboards
import states

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
async def pay_sub(callback : aiogram.types.CallbackQuery, state : aiogram.fsm.context.FSMContext):
    await callback.answer()
    await callback.message.edit_reply_markup(reply_markup=None)
    month_cost = int(open('sub_cost.txt').read())
    cost = open('sub_cost.txt').read()
    if callback.data == '1':
        description = 'Оплата подписки на 1 месяц'
        cost = month_cost
    elif callback.data == '3':
        description = 'Оплата подписки на 3 месяца'
        cost = month_cost * 3 // 100 * 85
    elif callback.data == '6':
        description = 'Оплата подписки на 6 месяцев'
        cost = month_cost * 6 // 100 * 70
    await state.set_state(None)
    await callback.message.answer_invoice(
        title='VPN',
        description=description,
        payload='payload',
        currency='RUB',
        prices=[
            {
                'label': 'Подписка',
                'amount': f'{cost}00'
            }
        ],
        provider_token='390540012:LIVE:55912',
        need_email=True,
        send_email_to_provider=True,
        provider_data=json.dumps(
            {
                'receipt': {
                    'items': [
                        {
                            'description': description,
                            'quantity': '1.00',
                            'amount': {
                                'value': f'{cost}.00',
                                'currency': 'RUB'
                            },
                            'vat_code': 1
                        }
                    ]
                }
            }
        )
    )


@router.pre_checkout_query()
async def precheck(query : aiogram.types.PreCheckoutQuery, bot : aiogram.Bot):
    await bot.answer_pre_checkout_query(query.id, ok=True)


@router.message(aiogram.F.content_type==aiogram.types.ContentType.SUCCESSFUL_PAYMENT)
async def get_payment(message : aiogram.types.Message):
    utils.set_user_subscription(
        message.from_user.id,
        1,
        (dt.datetime.now() + dt.timedelta(days=30)).isoformat()
    )
    await message.answer(
        'Оплата произведена успешно!\nИнструкция по подключению VPN - /instruction\nУправление устройствами - /management'
    )
