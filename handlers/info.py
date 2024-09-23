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
    await message.answer(text=answers.start)


@router.message(aiogram.F.text=='/subinfo')
async def about_sub_message(message : aiogram.types.Message):
    await message.answer(answers.subinfo.replace('{cost}', open('sub_cost.txt').read()))


@router.message(aiogram.F.text=='/instruction')
async def instruction_message(message : aiogram.types.Message):
    await message.answer(answers.instruction, parse_mode='HTML')


@router.message(aiogram.F.text=='/vpninfo')
async def instruction_message(message : aiogram.types.Message):
    await message.answer(answers.vpninfo)
