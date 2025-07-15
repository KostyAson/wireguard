import aiogram
import aiogram.filters
import answers
import utils
import log
import datetime as dt
import os

router = aiogram.Router()


@router.message(aiogram.filters.CommandStart())
async def start_message(message : aiogram.types.Message, command : aiogram.filters.CommandObject):
    log.logger.info(f"Пользователь {utils.get_user_username(message)} отправил комманду start")
    if not utils.check_user_in_db(message.from_user.id):
        if command.args is not None:
            refer = command.args.split()[0]
        else:
            refer = None
        if refer is not None and refer[:2] == 'ad':
            ad_id = int(refer[2:])
            refer = None
            ad_info = utils.get_ad_info(ad_id)
            if utils.get_count_ad(ad_id) == ad_info[2]:
                ad_id = None
            else:
                if ad_info[4].lower() != "none":
                    await message.answer(text=ad_info[4])
        else:
            ad_id = None
        name = utils.get_user_username(message)
        utils.add_user(message.from_user.id, name, refer, ad_id)
        if ad_id is not None and ad_info[3] is not None:
            days = ad_info[3]
        else:
            days = 7
        await message.answer(text=answers.start_with_sub.replace('{days}', str(days)), parse_mode='HTML', disable_web_page_preview=True)
        utils.set_user_subscription(message.from_user.id, 1, (dt.datetime.now() + dt.timedelta(days=days)).isoformat())

        #  добавление устройства "start"
        utils.add_device(message.from_user.id, 'start', name)
        normal_name = utils.get_normal_device_name('start')
        os.system(f'qrencode -t png -s 10 -m 1 -o qr.png < {normal_name}.conf')
        await message.answer_document(
            aiogram.types.input_file.FSInputFile(f'{normal_name}.conf'),
            caption=f'Файл для подключения к VPN\n\nИнструкция по подключению выше 👆'
        )
        await message.answer_photo(
            photo=aiogram.types.FSInputFile(f'qr.png'),
            caption=f'QR для подключения к VPN\n\nИнструкция по подключению выше 👆'
        )
        os.system(f'rm "{normal_name}.conf" && rm "qr.png"')
    else:
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
