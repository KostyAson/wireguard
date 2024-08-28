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


def add_user(user_id, username):
    conn = sqlite3.connect('db.sqlite')
    cur = conn.cursor()
    cur.execute(f'INSERT INTO users(id, subscription, username) VALUES({user_id}, 0, "{username}");')
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
    work = 1 if len(get_user_devices(user_id)) < 2 else 0
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
    cur.execute(f'SELECT address, public_key FROM devices WHERE work=1;')
    data = cur.fetchall()
    cur.close()
    conn.close()
    config = open('server.conf').read().strip()
    for x in data:
        config += f'\n[PEER]\nPublicKey = {x[1]}\nAllowedIPs = {x[0]}'
    config_file = open('wg0.conf', 'w')
    config_file.write(config)
    config_file.close()
    '''os.system('wg-quick strip wg0 > strip.txt')
    os.system('wg syncconf wg0 strip.txt')
    os.system('rm strip.txt')'''


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
                cur.execute(f'UPDATE devices SET work=0 WHERE user_id={id};')
                await bot.send_message(id, 'Истек срок действия вашей подписки\nОплатить подписку - /pay')
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
