import aiogram
import aiogram.filters

router = aiogram.Router()


@router.message(aiogram.F.text=='/ref')
async def about_sub_message(message : aiogram.types.Message):
    await message.answer(
        f'У нас действует реферальная система.\n\nЕсли пользователь перешел в бота по вашей ссылке, вы получаете столько недель подписки, сколько месяцев подписки купил данный пользователь.\nВаша реферальная ссылка:\nhttps://t.me/AVPNmanagerBot?start={message.from_user.id}'
    )
