import sqlite3
import os
import dotenv
import datetime as dt
import asyncio
import aiogram
import transliterate

dotenv.load_dotenv('.env')


def check_user_sub(user_id):
    conn = sqlite3.connect('db.sqlite')
    cur = conn.cursor()
    cur.execute(f'SELECT subscription FROM users WHERE id={user_id};')
    data = cur.fetchone()[0]
    cur.close()
    conn.close()
    return data


def get_user_subdate(user_id):
    conn = sqlite3.connect('db.sqlite')
    cur = conn.cursor()
    cur.execute(f'SELECT subdate FROM users WHERE id={user_id};')
    data = cur.fetchone()[0]
    cur.close()
    conn.close()
    return data


def add_user(user_id, username, refer):
    conn = sqlite3.connect('db.sqlite')
    cur = conn.cursor()
    if refer is None:
        cur.execute(f'INSERT INTO users(id, subscription, username) VALUES({user_id}, 0, "{username}");')
    else:
        cur.execute(f'INSERT INTO users(id, subscription, username, from_user) VALUES({user_id}, 0, "{username}", {refer});')
    conn.commit()
    cur.close()
    conn.close()


def set_user_subscription(user_id, subscription, subdate=None):
    conn = sqlite3.connect('db.sqlite')
    cur = conn.cursor()
    cur.execute(f'UPDATE users SET subscription={subscription},subdate="{subdate}" WHERE id={user_id};')
    conn.commit()
    cur.close()
    conn.close()


def get_user_devices(user_id):
    conn = sqlite3.connect('db.sqlite')
    cur = conn.cursor()
    cur.execute(f'SELECT name, work, id FROM devices WHERE user_id={user_id};')
    data = cur.fetchall()
    cur.close()
    conn.close()
    return data


def add_device(user_id, name, username):
    conn = sqlite3.connect('db.sqlite')
    cur = conn.cursor()
    work = 1
    name = get_normal_device_name(name)
    os.system(f'wg genkey | tee {name}_private.key | wg pubkey > {name}_public.key')
    private = open(f'{name}_private.key').read().strip()
    public = open(f'{name}_public.key').read().strip()
    os.system(f'rm {name}_private.key && rm {name}_public.key')
    address = get_free_address()
    cur.execute(f'INSERT into devices(user_id, name, work, public_key, private_key, address, username) VALUES({user_id}, "{name}", {work}, "{public}", "{private}", "{address}", "{username}");')
    conn.commit()
    cur.close()
    conn.close()
    conf = open('device.conf').read().replace('{private}', private).replace('{address}', address).replace('{ip}', os.getenv('ip'))
    file_conf = open(f'{name}.conf', 'w+')
    file_conf.write(conf)
    file_conf.close()
    if work:
        update_server_config()


def update_server_config():
    conn = sqlite3.connect('db.sqlite')
    cur = conn.cursor()
    users = [str(x[0]) for x in cur.execute('SELECT id FROM users WHERE subscription=1;').fetchall()]
    cur.execute(f'SELECT address, public_key FROM devices WHERE work=1 AND user_id IN ({", ".join(users)});')
    data = cur.fetchall()
    cur.close()
    conn.close()
    config = open('server.conf').read().strip()
    for x in data:
        config += f'\n[PEER]\nPublicKey = {x[1]}\nAllowedIPs = {x[0]}'
    config_file = open('wg0.conf', 'w')
    config_file.write(config)
    config_file.close()
    os.system('wg-quick strip wg0 > strip.txt')
    os.system('wg syncconf wg0 strip.txt')
    os.system('rm strip.txt')


def get_free_address():
    conn = sqlite3.connect('db.sqlite')
    cur = conn.cursor()
    cur.execute(f'SELECT address FROM devices;')
    data = cur.fetchall()
    cur.close()
    conn.close()
    addresses = set([address[0] for address in data])
    for i in range(2, 256):
        for j in range(0, 256):
            if f'10.0.{i}.{j}/32' not in addresses:
                return f'10.0.{i}.{j}/32'


def delete_device(device_id):
    conn = sqlite3.connect('db.sqlite')
    cur = conn.cursor()
    cur.execute(f'DELETE from devices WHERE id={device_id} LIMIT 1;')
    conn.commit()
    cur.close()
    conn.close()
    update_server_config()


def change_work_device(device_id, work):
    conn = sqlite3.connect('db.sqlite')
    cur = conn.cursor()
    cur.execute(f'UPDATE devices SET work={work} WHERE id={device_id};')
    conn.commit()
    cur.close()
    conn.close()
    update_server_config()


def get_device_file(device_id):
    conn = sqlite3.connect('db.sqlite')
    cur = conn.cursor()
    cur.execute(f'SELECT address, private_key, name FROM devices WHERE id={device_id};')
    address, private, name = cur.fetchone()
    cur.close()
    conn.close()
    conf = open('device.conf').read().replace('{private}', private).replace('{address}', address).replace('{ip}', os.getenv('ip'))
    file_conf = open(f'{get_normal_device_name(name)}.conf', 'w+')
    file_conf.write(conf)
    file_conf.close()
    return name


def get_count_user_work_devices(user_id):
    conn = sqlite3.connect('db.sqlite')
    cur = conn.cursor()
    cur.execute(f'SELECT name, work, id FROM devices WHERE user_id={user_id} AND work=1;')
    data = cur.fetchall()
    cur.close()
    conn.close()
    return len(data)


async def control_sub(bot : aiogram.Bot):
    while True:
        conn = sqlite3.connect('db.sqlite')
        cur = conn.cursor()
        cur.execute(f'SELECT id, subdate FROM users WHERE subscription=1;')
        data = cur.fetchall()
        for id, date in data:
            date = dt.datetime.fromisoformat(date)
            if dt.datetime.now() >= date:
                cur.execute(f'UPDATE users SET subscription=0 WHERE id={id};')
                try:
                    await bot.send_message(id, 'Истек срок действия вашей подписки\nОплатить подписку - /pay')
                except:
                    pass
        conn.commit()
        cur.close()
        conn.close()
        update_server_config()
        await asyncio.sleep(3600)


def check_user_in_db(user_id):
    conn = sqlite3.connect('db.sqlite')
    cur = conn.cursor()
    cur.execute(f'SELECT id FROM users WHERE id={user_id};')
    data = cur.fetchall()
    cur.close()
    conn.close()
    return bool(len(data))


def get_normal_device_name(name):
    return transliterate.translit(name.replace(' ', '-'), language_code='ru', reversed=True)


def get_user_use_free_sub(user_id):
    conn = sqlite3.connect('db.sqlite')
    cur = conn.cursor()
    cur.execute(f'SELECT free_sub_used FROM users WHERE id={user_id};')
    data = cur.fetchone()
    cur.close()
    conn.close()
    return bool(data[0] is None)


def set_user_use_free_sub(user_id):
    conn = sqlite3.connect('db.sqlite')
    cur = conn.cursor()
    cur.execute(f'UPDATE users SET free_sub_used=1 WHERE id={user_id};')
    conn.commit()
    cur.close()
    conn.close()


def get_user_ref(user_id):
    conn = sqlite3.connect('db.sqlite')
    cur = conn.cursor()
    cur.execute(f'SELECT from_user FROM users WHERE id={user_id};')
    data = cur.fetchone()
    cur.close()
    conn.close()
    return data[0]


def grand_ref_sub(ref_id, sub):
    conn = sqlite3.connect('db.sqlite')
    cur = conn.cursor()
    if check_user_sub(ref_id):
        cur.execute(f'SELECT subdate FROM users WHERE id={ref_id};')
        date = dt.datetime.fromisoformat(cur.fetchone()[0])
        date += dt.timedelta(days=7 * sub)
        ans = True
    else:
        date = dt.datetime.now()
        date += dt.timedelta(days=7 * sub)
        ans = False
    cur.execute(f'UPDATE users SET subscription=1,subdate="{date.isoformat()}" WHERE id={ref_id};')
    conn.commit()
    cur.close()
    conn.close()
    return ans


def get_payers():
    conn = sqlite3.connect('db.sqlite')
    cur = conn.cursor()
    cur.execute('SELECT * FROM users WHERE subscription=1 AND subdate!="2050-09-26T23:15:43.227305";')
    data = cur.fetchall()
    cur.close()
    conn.close()
    return len(data) * 200


def get_all_users():
    conn = sqlite3.connect('db.sqlite')
    cur = conn.cursor()
    cur.execute('SELECT id FROM users WHERE subscription=1;')
    data = cur.fetchall()
    cur.close()
    conn.close()
    return list(map(lambda x : x[0], data))


def get_user_username(message):
    name = message.from_user.username
    if name is None:
        name = str(message.from_user.first_name) + " " + str(message.from_user.last_name)
    return name


def get_users_subscriptions():
    db = sqlite3.connect('db.sqlite')
    cur = db.cursor()
    cur.execute("SELECT subdate, username FROM users WHERE subscription=1;")
    data = map(lambda x : (dt.datetime.fromisoformat(x[0]), x[1]), cur.fetchall())
    data = sorted(filter(lambda x : x[0] < dt.datetime(year=2050, month=1, day=1), data))
    s = ''
    for x in data:
        total = (x[0] - dt.datetime.now()).total_seconds()
        days = int(total / 60 / 60 / 24)
        s += f'{days}:{int((total - days * 24 * 60 * 60) / 60 / 60)} @{x[1]}\n'
    cur.close()
    db.close()
    return s[:-1]


def add_ad(title, description, limit, free_time, message):
    db = sqlite3.connect('db.sqlite')
    cur = db.cursor()
    cur.execute(f'INSERT INTO ads(title, description, limit, free_time, message) VALUES("{title}", "{description}", {limit}, {free_time}, "{message}");')
    db.commit()
    return cur.lastrowid()
