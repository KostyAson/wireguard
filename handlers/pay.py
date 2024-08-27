import aiogram
import utils
import json

router = aiogram.Router()


@router.message(aiogram.F.text=='/pay')
async def invoicing(message : aiogram.types.Message):
    await message.answer_invoice(
        title='VPN',
        description='Оплата подписки на месяц',
        payload='payload',
        currency='RUB',
        prices=[
            {
                'label': 'Подписка',
                'amount': '20000'
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
                            'description': 'подписка VPN на месяц',
                            'quantity': '1.00',
                            'amount': {
                                'value': '200.00',
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
    utils.set_user_subscription(message.from_user.id, 1)
    await message.answer(
        'Оплата произведена успешно!\nИнструкция по подключению VPN - /instruction\nУправление устройствами - /management'
    )
