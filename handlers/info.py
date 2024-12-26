import aiogram
import aiogram.filters
import answers
import utils

router = aiogram.Router()


@router.message(aiogram.filters.CommandStart())
async def start_message(message : aiogram.types.Message, command : aiogram.filters.CommandObject):
    if not utils.check_user_in_db(message.from_user.id):
        if command.args is not None:
            refer = command.args.split()[0]
        else:
            refer = None
        name = message.from_user.username
        if name is None:
            name = str(message.from_user.first_name + " " + message.from_user.last_name)
        utils.add_user(message.from_user.id, name, refer)
    await message.answer(text=answers.start, parse_mode='HTML', disable_web_page_preview=True)


@router.message(aiogram.F.text=='/instruction')
async def instruction_message(message : aiogram.types.Message):
    await message.answer(answers.instruction, parse_mode='HTML', disable_web_page_preview=True)


@router.message(aiogram.F.text=='/ref')
async def about_sub_message(message : aiogram.types.Message):
    await message.answer(
        f'У нас действует реферальная система 🤝\n\nЕсли пользователь перешел в бота по вашей ссылке, а после оплатил подписку на N месяцев, мы начислим вам N недель подписки\n\nВаша реферальная ссылка:\nhttps://t.me/AVPNmanagerBot?start={message.from_user.id}\n\n'
    )
