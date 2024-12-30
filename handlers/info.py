import aiogram
import aiogram.filters
import answers
import utils
import log

router = aiogram.Router()


@router.message(aiogram.filters.CommandStart())
async def start_message(message : aiogram.types.Message, command : aiogram.filters.CommandObject):
    log.logger.info(f"Пользователь {utils.get_user_username(message)} отправил комманду start")
    if not utils.check_user_in_db(message.from_user.id):
        if command.args is not None:
            refer = command.args.split()[0]
        else:
            refer = None
        name = utils.get_user_username(message)
        utils.add_user(message.from_user.id, name, refer)
    await message.answer(text=answers.start, parse_mode='HTML', disable_web_page_preview=True)


@router.message(aiogram.F.text=='/instruction')
async def instruction_message(message : aiogram.types.Message):
    log.logger.info(f"Пользователь {utils.get_user_username(message)} отправил комманду instruction")
    await message.answer(answers.instruction, parse_mode='HTML', disable_web_page_preview=True)


@router.message(aiogram.F.text=='/ref')
async def about_sub_message(message : aiogram.types.Message):
    log.logger.info(f"Пользователь {utils.get_user_username(message)} отправил комманду ref")
    await message.answer(
        answers.ref_system.replace('{id}', str(message.from_user.id)),
        disable_web_page_preview=True
    )
