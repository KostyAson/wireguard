import aiogram
import states
import aiogram.fsm
import aiogram.fsm.context
import utils
import sqlite3
import os
import asyncio
import answers
import datetime as dt

router = aiogram.Router()


@router.message(aiogram.F.text=='/admin')
async def admin(message : aiogram.types.Message):
    if message.from_user.id == 2096978507:
        await message.answer(
'''
Выдать подписку - /grand_sub
Количество пользователей открывших бота - /count_all_users
Количество пользователей с подпиской - /count_users
Изменить цену подписки - /change_cost
Статистика устройств - /devices_stats
Средняя выручка за месяц - /average_revenue
Рассылка сообщений - /send_message
Добавить ip адреса в русские - /add_ip
Отправить сообщение конкретному пользователю - /send_to_user
Получить сроки подписок пользователей - /get_users_subscriptions
Добавить рекламу - /add_ad
Получить информацию о рекламах - /get_ads_info
Удалить рекламу - /del_ad
Запустить скидку для неоплативших пользователей - /make_discount
'''
        )
    else:
        await message.answer(
            'У вас нет доступа к админке'
        )


@router.message(aiogram.F.text=='/grand_sub')
async def grand_sub_command(message : aiogram.types.Message, state : aiogram.fsm.context.FSMContext):
    await state.set_state(states.AdminState.grand_sub)
    await message.answer(
        'Отправьте сообщение в формате\n{id} {срок в днях}'
    )


@router.message(states.AdminState.grand_sub)
async def grand_sub(message : aiogram.types.Message, state : aiogram.fsm.context.FSMContext):
    await state.set_state(None)
    id, days = message.text.split()
    days = int(days)
    if message.from_user.id == 2096978507:
        utils.set_user_subscription(
            id,
            bool(days),
            (dt.datetime.now() + dt.timedelta(days=days)).isoformat()
        )
        await message.answer('Подписка выдана')
        utils.update_server_config()
    else:
        await message.answer('Отказано в доступе')


@router.message(aiogram.F.text == '/count_all_users')
async def count_all_users(message : aiogram.types.Message):
    if message.from_user.id == 2096978507:
        conn = sqlite3.connect('db.sqlite')
        cur = conn.cursor()
        cur.execute('SELECT id FROM users;')
        await message.answer(
            str(len(cur.fetchall()))
        )
        cur.close()
        conn.close()
    else:
        await message.answer('Отказано в доступе')


@router.message(aiogram.F.text == '/count_users')
async def count_users(message : aiogram.types.Message):
    if message.from_user.id == 2096978507:
        conn = sqlite3.connect('db.sqlite')
        cur = conn.cursor()
        cur.execute('SELECT id FROM users WHERE subscription=1;')
        await message.answer(
            str(len(cur.fetchall()))
        )
        cur.close()
        conn.close()
    else:
        await message.answer('Отказано в доступе')


@router.message(aiogram.F.text == '/change_cost')
async def set_cost(message : aiogram.types.Message, state : aiogram.fsm.context.FSMContext):
    if message.from_user.id == 2096978507:
        await state.set_state(states.AdminState.set_sub_cost)
        await message.answer(
            'Введите новую стоимость подписки'
        )
    else:
        await message.answer('Отказано в доступе')


@router.message(states.AdminState.set_sub_cost)
async def set_sub_cost(message : aiogram.types.Message, state : aiogram.fsm.context.FSMContext):
    await state.set_state(None)
    if message.from_user.id == 2096978507:
        try:
            file = open('sub_cost.txt', 'w')
            file.write(message.text)
            file.close()
        except Exception as e:
            print(e)
        await message.answer('Стоимость изменена')
    else:
        await message.answer('Отказано в доступе')


@router.message(aiogram.F.text == '/devices_stats')
async def devices_stats(message : aiogram.types.Message):
    if message.from_user.id == 2096978507:
        os.system('wg show > stats.txt')
        stats = open('stats.txt').readlines()
        os.system('rm stats.txt')
        conn = sqlite3.connect('db.sqlite')
        cur = conn.cursor()
        cur.execute('SELECT public_key, username, name FROM devices;')
        data = cur.fetchall()
        cur.close()
        conn.close()
        dic = {}
        for x in data:
            dic[x[0]] = str(x[2]) + ' @' + str(x[1])
        ans = ''
        c = 0
        for s in stats:
            s = s.strip()
            if 'endpoint' in s or 'allowed ips' in s:
                continue
            s = s.replace('latest handshake: ', '').replace('transfer: ', '')
            if s[:4] == 'peer':
                public_key = s.split()[1]
                if public_key not in dic:
                    continue
                s = dic[public_key]
            ans += s + '\n'
            if c % 20 == 0 and c != 0:
                await message.answer(ans)
                ans = ''
            c += 1
        if ans:
            await message.answer(ans)
    else:
        await message.answer('В доступе отказано')


@router.message(aiogram.F.text == '/average_revenue')
async def average_revenue(message : aiogram.types.Message):
    if message.from_user.id == 2096978507:
        await message.answer(str(utils.get_payers()))
    else:
        await message.answer('Отказано в доступе')


@router.message(aiogram.F.text == '/send_message')
async def get_send_message(message : aiogram.types.Message, state : aiogram.fsm.context.FSMContext):
    if message.from_user.id == 2096978507:
        await message.answer('Напишите сообщение для пользователей')
        await state.set_state(states.AdminState.send_message)
    else:
        await message.answer('Отказано в доступе')


@router.message(states.AdminState.send_message)
async def send_message(message : aiogram.types.Message,
                       bot : aiogram.Bot,
                       state : aiogram.fsm.context.FSMContext):
    for id in utils.get_all_users():
        try:
            await bot.send_message(chat_id=id, text=message.text)
        except:
            continue
        await asyncio.sleep(0.1)
    await state.set_state(None)


@router.message(aiogram.F.text=='/add_ip')
async def add_ip_command(message : aiogram.types.Message, state : aiogram.fsm.context.FSMContext):
    if message.from_user.id == 2096978507:
        await message.answer('Отправьте список ip')
        await state.set_state(states.AdminState.add_ip)
    else:
        await message.answer('Отказано в доступе')


@router.message(states.AdminState.add_ip)
async def add_ip(message : aiogram.types.Message, state : aiogram.fsm.context.FSMContext):
    for ip in message.text.split():
        os.system(
    f'target_ip="{ip}/32"\n' + 
    '''gateway=`ip route | awk '/default/ {print $3; exit}'`
    gateway_device=`ip route | awk '/default/ {print $5; exit}'`
    ip route add $target_ip via $gateway dev $gateway_device
    ''')
    await message.answer('ip добавлены')
    await state.set_state(None)


@router.message(aiogram.F.text=='/send_to_user')
async def send_to_user(message : aiogram.types.Message, state : aiogram.fsm.context.FSMContext):
    await state.set_state(states.AdminState.grand_sub)
    await message.answer(
        'На первой строке отправьте id пользователя, начиная со второй само сообщение'
    )
    await state.set_state(states.AdminState.send_to_user)


@router.message(states.AdminState.send_to_user)
async def send_message_to_user(message : aiogram.types.Message,
                       bot : aiogram.Bot,
                       state : aiogram.fsm.context.FSMContext):
    id = int(message.text.split('\n')[0])
    text = '\n'.join(message.text.split('\n')[1:])
    await bot.send_message(chat_id=id, text=text)
    await state.set_state(None)


@router.message(aiogram.F.text=='/get_users_subscriptions')
async def get_users_subscriptions(message : aiogram.types.Message):
    if message.from_user.id == 2096978507:
        s = utils.get_users_subscriptions().split('\n')
        for i in range(0, len(s), 50):
            await message.answer(text='\n'.join(s[i:i + 50]))
            i += 50


@router.message(aiogram.F.text=='/add_ad')
async def add_ad(message : aiogram.types.Message, state : aiogram.fsm.context.FSMContext):
    if message.from_user.id != 2096978507:
        return
    await state.set_state(states.AddAdState.get_title)
    await message.answer('Напишите название')


@router.message(states.AddAdState.get_title)
async def get_title_ad(message : aiogram.types.Message, state : aiogram.fsm.context.FSMContext):
    await state.update_data(title=message.text)
    await state.set_state(states.AddAdState.get_description)
    await message.answer('Напишите описание, или None если не надо')


@router.message(states.AddAdState.get_description)
async def get_description_ad(message : aiogram.types.Message, state : aiogram.fsm.context.FSMContext):
    if message.text.lower() == 'none':
        data = None
    else:
        data = message.text
    await state.update_data(description=data)
    await state.set_state(states.AddAdState.get_limit)
    await message.answer('Напишите лимит, или None если не надо')


@router.message(states.AddAdState.get_limit)
async def get_limit_ad(message : aiogram.types.Message, state : aiogram.fsm.context.FSMContext):
    if message.text.lower() == 'none':
        data = None
    else:
        data = int(message.text)
    await state.update_data(limit=data)
    await state.set_state(states.AddAdState.get_free_time)
    await message.answer('Напишите пробный период (в днях), или None если не надо')


@router.message(states.AddAdState.get_free_time)
async def get_free_time_ad(message : aiogram.types.Message, state : aiogram.fsm.context.FSMContext):
    if message.text.lower() == 'none':
        data = None
    else:
        data = int(message.text)
    await state.update_data(free_time=data)
    await state.set_state(states.AddAdState.get_message)
    await message.answer('Напишите добавочное сообщение при старте, или None если не надо')


@router.message(states.AddAdState.get_message)
async def get_message_ad(message : aiogram.types.Message, state : aiogram.fsm.context.FSMContext):
    if message.text.lower() == 'none':
        data = None
    else:
        data = message.text
    await state.update_data(message=data)
    await state.set_state(None)
    data = await state.get_data()
    ad_id = utils.add_ad(
        data['title'],
        data['description'],
        data['limit'],
        data['free_time'],
        data['message']
    )
    await message.answer(f'Реклама добавлена')
    url = f'https://t.me/AVPNmanagerBot?start=ad{ad_id}'
    await message.answer(answers.ad.replace('{url}', url).replace('{days}', str(data['free_time'])), parse_mode='HTML')


@router.message(aiogram.F.text=='/get_ads_info')
async def get_ads_info(message : aiogram.types.Message):
    if message.from_user.id == 2096978507:
        ids = utils.get_all_ads()
        for id in ids:
            data = utils.get_ad_info(int(id[0]))
            count_clicks = utils.get_count_ad(int(id[0]))
            count_users = len(utils.get_ad_users(int(id[0])))
            await message.answer(
                text=f'title: {data[0]}\n\ndescription: {data[1]}\n\nlimit: {data[2]}\n\nfree_time: {data[3]}\n\nmessage: {data[4]}\n\ncount clicks: {count_clicks}\n\ncount users: {count_users}\n\npayers: {data[5]}\n\nurl: https://t.me/AVPNmanagerBot?start=ad{id[0]}',
            )
            await asyncio.sleep(0.5)


@router.message(aiogram.F.text=='/del_ad')
async def del_add(message : aiogram.types.Message, state : aiogram.fsm.context.FSMContext):
    if message.from_user.id == 2096978507:
        await message.answer('Отправьте ID рекламного объявления для удаления')
        await state.set_state(states.AdminState.del_add)


@router.message(states.AdminState.del_add)
async def get_del_add(message : aiogram.types.Message, state : aiogram.fsm.context.FSMContext):
    utils.del_add(message.text)
    await message.answer('Объявление удалено')
    await state.set_state(None)


@router.message(aiogram.F.text == '/mailing')
async def mailing(message : aiogram.types.Message, bot : aiogram.Bot):
    if message.from_user.id != 2096978507:
        return
    c = 0
    for user in utils.get_not_start_users():
        id = user[0]
        name = user[1]
        if id in [7180445157]:
            continue
        utils.set_user_subscription(id, 1, (dt.datetime.now() + dt.timedelta(days=7)).isoformat())
        try:
            await bot.send_message(chat_id=id, text=answers.mailing, parse_mode='HTML', disable_web_page_preview=True)
            #  добавление устройства "start"
            utils.add_device(id, 'start', name)
            normal_name = utils.get_normal_device_name('start')
            os.system(f'qrencode -t png -s 10 -m 1 -o qr.png < {normal_name}.conf')
            await bot.send_document(
                document=aiogram.types.input_file.FSInputFile(f'{normal_name}.conf'),
                caption=f'Файл для подключения к VPN\n\nИнструкция по подключению выше 👆',
                chat_id=id
            )
            await bot.send_photo(
                photo=aiogram.types.FSInputFile(f'qr.png'),
                caption=f'QR для подключения к VPN\n\nИнструкция по подключению выше 👆',
                chat_id=id
            )
            os.system(f'rm "{normal_name}.conf" && rm "qr.png"')
            c += 1
        except:
            pass
        await asyncio.sleep(0.2)
    await message.answer(f'Удачных сообщений {c} из {len(utils.get_not_start_users())}')


@router.message(aiogram.F.text == '/make_discount')
async def make_discount(message : aiogram.types.Message, bot : aiogram.Bot):
    db = sqlite3.connect('db.sqlite')
    cur = db.cursor()
    cur.execute('SELECT id FROM users WHERE subscription=0 AND start=1;')
    ids = cur.fetchall()
    for id in ids:
        cur.execute(f'UPDATE users SET low_cost=1 WHERE id={id[0]};')
    db.commit()
    cur.close()
    db.close()
    c = 0
    for id in ids:
        try:
            await bot.send_message(
                chat_id=id[0],
                text=f'Здравствуйте! 👋\n\nМы заметили, что вы пользовались нашим VPN, но не стали продлевать подписку.\n\nСпециально для вас мы делаем персональную скидку ❗️\n\n<b><s>199р</s> 99р 💸</b>\n\nОплачивайте подписку, и пользуйтесь свободным интернетом без ограничений - <b>/pay</b>',
                parse_mode='HTML'
            )
            c += 1
        except:
            pass
        await asyncio.sleep(0.1)
    await message.answer(text=f'Удачных сообщений: {c}')
