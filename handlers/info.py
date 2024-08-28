import aiogram
import aiogram.filters
import answers
import utils

router = aiogram.Router()


@router.message(aiogram.F.text=='/start')
async def start_message(message : aiogram.types.Message):
    if not utils.check_user_in_db(message.from_user.id):
        name = message.from_user.username
        if name is None:
            name = message.from_user.first_name + " " + message.from_user.last_name
        utils.add_user(message.from_user.id, name)
    await message.answer(text=answers.start)


@router.message(aiogram.F.text=='/subinfo')
async def about_sub_message(message : aiogram.types.Message):
    await message.answer(answers.subinfo.replace('{cost}', open('sub_cost.txt').read()))


@router.message(aiogram.F.text=='/instruction')
async def instruction_message(message : aiogram.types.Message):
    await message.answer(answers.instruction, parse_mode='HTML')
