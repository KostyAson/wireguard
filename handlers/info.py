import aiogram
import aiogram.filters
import answers
import utils

router = aiogram.Router()


@router.message(aiogram.F.text=='/start')
async def start_message(message : aiogram.types.Message):
    utils.add_user(message.from_user.id)
    await message.answer(text=answers.start)


@router.message(aiogram.F.text=='/subinfo')
async def about_sub_message(message : aiogram.types.Message):
    await message.answer(answers.subinfo)


@router.message(aiogram.F.text=='/instruction')
async def instruction_message(message : aiogram.types.Message):
    await message.answer(answers.instruction, parse_mode='HTML')
