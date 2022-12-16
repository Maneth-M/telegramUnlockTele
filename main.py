from telethon import TelegramClient, sync, events, functions
from config import Config
import os
import sqlite3


client = TelegramClient("sessions/main", Config.api_id, Config.api_hash)
client.start()

@client.on(events.NewMessage())
async def new_message_handler(event):

    # if event.peer_id.user.id == 5551343333:
    if event.peer_id.user_id == 1585124712 or event.peer_id.user_id == 5551343333:
        if "/add" in event.raw_text:
            try:
                x = int(event.raw_text.replace('/add', '').strip())
                connection = sqlite3.connect('data.db')
                cursor = connection.cursor()
                cursor.execute(f"INSERT INTO users VALUES({x})")
                connection.commit()
                cursor.execute("SELECT * FROM users")
                connection.close()
                await event.reply(f"User {x} Added")
            except Exception as e:
                if "UNIQUE constraint failed: users.userID" in e.args:
                    await event.reply("User Already Exists")
                else:
                    await event.reply("Unexpected Error. Please Check the ID")
        if "/remove" in event.raw_text:
            try:
                x = int(event.raw_text.replace('/remove', '').strip())
                connection = sqlite3.connect('data.db')
                cursor = connection.cursor()
                cursor.execute(f"DELETE FROM users WHERE userID = {x}")
                connection.commit()
                cursor.execute("SELECT * FROM users")
                connection.close()
                await event.reply(f"User {x} Removed")
            except:
                await event.reply("Unexpected Error. Please Check the ID")

    connection = sqlite3.connect('data.db')
    cursor = connection.cursor()
    ids = cursor.execute(f"SELECT userID FROM users WHERE userID = {event.peer_id.user_id}").fetchone()
    if ids:
        if event.raw_text.strip() == "/help":
            await event.reply(Config.help_message)

        elif event.message.message == "":
            if ".session" in event.message.media.document.attributes[0].file_name:
                await event.message.download_media(f"sessions/{event.peer_id.user_id}.session")
                await event.reply("Session Saved")

        elif "https://t.me/" in event.message.message:
            link = event.message.message.strip()
            attr = link.split("/")
            if len(attr) == 6:
                channel_id = "-100" + attr[-2]
                post_id = attr[-1].split("-")
                temp_cli = TelegramClient(f"sessions/{event.peer_id.user_id}", Config.api_id, Config.api_hash)
                await temp_cli.connect()
                if await temp_cli.is_user_authorized():
                    if len(post_id) == 1 or len(post_id) == 2 and not len(post_id) == 0:
                        post_id = [eval(i) for i in post_id]
                        try:
                            channel = await temp_cli.get_entity(int(channel_id))
                            if len(post_id) == 1:
                                msgs = await temp_cli.get_messages(channel, ids=int(post_id[0]))
                                msgs = [msgs]
                            else:
                                msgs = await temp_cli.get_messages(channel, ids=list(range(min(post_id), max(post_id)+1)))

                            for msg in msgs:
                                try:
                                    await event.reply(f"Downloading the File - {msg.id}")
                                    await msg.download_media(f"media/{event.peer_id.user_id}")
                                    await event.reply(f"Downloaded Successfully. Sending {msg.id}")
                                    try:
                                        for i in os.listdir("media"):
                                            if str(event.peer_id.user_id ) in i:
                                                await client.send_file(event.peer_id.user_id, f"media/{i}")
                                                os.remove(F"media/{i}")
                                                break
                                    except Exception as e:
                                        print(e)
                                        await event.reply("Unexpected Error")
                                except Exception as e:
                                    print(e)
                                    pass
                        except Exception as e:
                            print(e)
                            await event.reply("Failed. Please check the link and the session file again.")
                    else:
                        await event.reply("Unexpected Error. Please Check the link")
                else:
                    await event.reply("Please Login first. /help")
                temp_cli.disconnect()
            else:
                await event.reply("Invalid Link")
    else:
        await event.reply("Not Authorized. Please Contact @Views")


client.run_until_disconnected()
