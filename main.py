from telethon.sync import TelegramClient
from telethon import events, utils
from telethon.tl import types
from telethon import errors
from FastTelethon import download_file, upload_file
from config import Config
import os
import sqlite3
import phonenumbers
import time



client = TelegramClient("sessions/main", Config.api_id, Config.api_hash)
client.start()


@client.on(events.NewMessage(pattern="/start$"))
async def start_message(event):
    if os.path.isfile(f"sessions/{event.peer_id.user_id}.session"):
        temp_cli = TelegramClient(f"sessions/{event.peer_id.user_id}", Config.api_id, Config.api_hash)
        await temp_cli.connect()
        if await temp_cli.is_user_authorized():
            await event.reply("Please Send the url to the file")
        else:
            await event.reply("You are not authorized. please Sign in again.\n/signin")
        temp_cli.disconnect()
    else:
        connection = sqlite3.connect("data.db")
        cursor = connection.cursor()
        cursor.execute(f"""INSERT INTO users(ID) VALUES({event.peer_id.user_id})""")
        connection.commit()
        connection.close()
        await event.reply("Please Sign in first\n/signin")

@client.on(events.NewMessage(pattern="/signin$"))
async def signin_message(event):
    if os.path.isfile(f"sessions/{event.peer_id.user_id}.session"):
        await event.reply("Sending the Phone Number will remove your old session file.")
    await event.reply(Config.phone_request)


@client.on(events.NewMessage(pattern=Config.phone_regex))
async def get_phone(event):
    if phonenumbers.is_valid_number(phonenumbers.parse(event.raw_text)):
        temp_cli = TelegramClient(f"sessions/{event.peer_id.user_id}", Config.api_id, Config.api_hash)
        await temp_cli.connect()
        code_hash = await temp_cli.send_code_request(event.raw_text)
        code_hash = code_hash.phone_code_hash
        await event.reply(Config.code_request)
        await temp_cli.disconnect()
        connection = sqlite3.connect("data.db")
        cursor = connection.cursor()
        cursor.execute(f"""UPDATE users SET phone='{event.raw_text}',code_hash='{code_hash}' WHERE ID = {event.peer_id.user_id}""")
        connection.commit()
        # connection.close()
    else:
        await event.reply("Invalid Phone Number. Please Send again.")


@client.on(events.NewMessage(pattern="[0-9]{1}[' ']{1}[0-9]{1}[' ']{1}[0-9]{1}[' ']{1}[0-9]{1}[' ']{1}[0-9]{1}"))
async def get_code(event):

    connection = sqlite3.connect("data.db")
    cursor = connection.cursor()
    u_id, u_phone, u_code, u_password, u_hash =cursor.execute(f"""SELECT * FROM users WHERE ID = {event.peer_id.user_id}""").fetchone()
    u_code = event.raw_text.replace(" ", "")
    cursor.execute(f"""UPDATE users set code = {u_code} WHERE ID = {event.peer_id.user_id}""")
    connection.commit()

    await client.send_message(event.peer_id.user_id, "Logging in...")
    temp_cli = TelegramClient(f"sessions/{event.peer_id.user_id}", Config.api_id, Config.api_hash)
    await temp_cli.connect()
    try:
        await temp_cli.sign_in(phone=u_phone, code=u_code, phone_code_hash=u_hash)
    except errors.SessionPasswordNeededError:
        await client.send_message(event.peer_id.user_id, Config.password_request)
    if await temp_cli.is_user_authorized():
        await client.send_message(event.peer_id.user_id, "Signed in")
    else:
        await client.send_message(event.peer_id.user_id, "Sign in failed")
    temp_cli.disconnect()

@client.on(events.NewMessage(pattern="https://t.me"))
async def get_link(event):
    timer = Timer()
    msg = ""
    async def progress_bar(current, total, type_of="Progress - "):
        if timer.can_send():
            await msg.edit("{} {}%".format(type_of, round(current * 100 / total)))

    async def download_upload(file, temp_cli, msg, event, progress_bar=progress_bar, ):
        try:
            with open(f"media/{file.media.document.id}", "wb") as out:
                await download_file(temp_cli, file.media.document, out, progress_callback=progress_bar)

            await msg.edit("Finished downloading. Sending Now")

            with open(f"media/{file.media.document.id}", "rb") as out:
                res = await upload_file(client, out, progress_callback=progress_bar)

                media = types.InputMediaUploadedDocument(
                    file=res,
                    mime_type=file.media.document.mime_type,
                    attributes=(file.media.document.attributes),
                    # not needed for most files, thumb=thumb,
                    force_file=False
                )
                await event.reply(file=media)
                await msg.edit("Finished uploading")
                return True
        except:
            return False

    temp_cli = TelegramClient(f"sessions/{event.peer_id.user_id}", Config.api_id, Config.api_hash)
    await temp_cli.connect()
    if await temp_cli.is_user_authorized():
        is_multiple, channel_id, ids = scrap_link(event.raw_text)

        if channel_id:
            channel_entity = await temp_cli.get_entity(int(channel_id))
            if is_multiple:
                pass
            else:
                file = await temp_cli.get_messages(channel_entity, ids=ids)
                msg = await event.reply("Downloading Started")
                await download_upload(file=file, temp_cli=temp_cli, msg=msg, event=event)
                os.remove(f"media/{file.media.document.id}")

        else:
            await event.reply("Error. Please Check your link again")

    else:
        await event.reply("You are not authorized. please Sign in again.\n/signin")

    temp_cli.disconnect()



# Accounts with passwords login. For later development
'''
@client.on(events.NewMessage(pattern="/password"))
async def get_password(event):
    # try:
    connection = sqlite3.connect("data.db")
    cursor = connection.cursor()
    u_id, u_phone, u_code, u_password, u_hash =cursor.execute(f"""SELECT * FROM users WHERE ID = {event.peer_id.user_id}""").fetchone()
    u_password = event.raw_text.split(" ")[1]
    cursor.execute(f"""UPDATE users set password = '{u_password}' WHERE ID = {event.peer_id.user_id}""")
    connection.commit()

    temp_cli = TelegramClient(f"sessions/{event.peer_id.user_id}", api_id=Config.api_id, api_hash=Config.api_hash)
    await temp_cli.connect()
    print(u_password)
    # try:
    await temp_cli.sign_in(phone=u_phone, password=u_password, code=u_code, phone_code_hash=u_hash)
    # except Exception as e:
    #     print(e)
    if await temp_cli.is_user_authorized():
        await client.send_message(event.peer_id.user_id, "Signed in")
    else:
        await client.send_message(event.peer_id.user_id, "Sign in failed")
    # except Exception as e:
    #     print(e)

'''


def scrap_link(txt):
    lst = txt.split(" ")
    for i in lst:
        if "t.me" in i:
            if i[-1]== "/":
                i = i[:len(i)-1]
            i = i.split("/")
            if "-" in i[1]:
                is_multiple = True
                ids = i[-1].split("-")
                ids = [eval(i) for i in ids]
                ids = list(range(min(ids), max(ids)+1))
            else:
                ids = int(i[-1])
                is_multiple = False
            channel_id = "-100" + i[-2]
            return is_multiple, channel_id, ids
    else:
        return None, None, None

class Timer:
    def __init__(self, time_between=2):
        self.start_time = time.time()
        self.time_between = time_between

    def can_send(self):
        if time.time() > (self.start_time + self.time_between):
            self.start_time = time.time()
            return True
        return False



client.run_until_disconnected()
