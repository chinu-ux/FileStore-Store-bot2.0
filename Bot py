import uuid
from pyrogram import Client, filters
from pyrogram.types import Message
from config import API_ID, API_HASH, BOT_TOKEN, OWNER_ID, CHANNEL_ID, SESSION_NAME, BASE_URL
from db import Session, FileRecord, LinkGroup
from sqlalchemy.orm import scoped_session

app = Client(SESSION_NAME, api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

session = scoped_session(Session)

def gen_key():
    return uuid.uuid4().hex[:10]

@app.on_message(filters.command("start") & filters.private)
async def start_handler(client: Client, message: Message):
    # If start param present (deep link), send files/group
    args = message.text.split()
    if len(args) > 1 and args[1]:
        key = args[1]
        # check if it's a group link
        grp = session.query(LinkGroup).filter_by(key=key).first()
        if grp:
            keys = grp.file_keys.split(",")
            for k in keys:
                rec = session.query(FileRecord).filter_by(key=k).first()
                if rec:
                    await client.copy_message(chat_id=message.from_user.id,
                                              from_chat_id=CHANNEL_ID,
                                              message_id=rec.channel_message_id)
            return
        # else single file
        rec = session.query(FileRecord).filter_by(key=key).first()
        if rec:
            await client.copy_message(chat_id=message.from_user.id,
                                      from_chat_id=CHANNEL_ID,
                                      message_id=rec.channel_message_id)
            return
        await message.reply_text("Invalid or expired link.")
        return

    # Normal start
    await message.reply_text("This bot stores private files. Admins can /upload by sending files in private chat to the bot (only owner).")

# ADMIN upload: admin sends video/file to bot in private chat -> bot forwards to private channel and stores record
@app.on_message(filters.private & filters.document | filters.video)
async def upload_handler(client: Client, message: Message):
    if message.from_user.id != OWNER_ID:
        return await message.reply_text("Only admin can upload files.")
    # forward/copy to channel
    sent = await client.send_message(chat_id=OWNER_ID, text="Uploading to channel...")
    # we copy message to channel to preserve file, pyrogram's copy or send
    res = await client.send_video(CHANNEL_ID, message.video.file_id) if message.video else await client.send_document(CHANNEL_ID, message.document.file_id)
    # store DB
    key = gen_key()
    rec = FileRecord(key=key, channel_message_id=res.message_id, file_type='video' if message.video else 'document', title=message.caption or "")
    session.add(rec)
    session.commit()
    link = BASE_URL + key
    await message.reply_text(f"File uploaded. Link: {link}")

# /link command to create grouped link from multiple keys (admin)
@app.on_message(filters.command("link") & filters.private)
async def link_command(client: Client, message: Message):
    # Format: /link key1 key2 key3  (or you can implement to accept forwarded messages)
    if message.from_user.id != OWNER_ID:
        return
    parts = message.text.split()
    if len(parts) < 2:
        return await message.reply_text("Usage: /link <filekey1> <filekey2> ...")
    file_keys = parts[1:]
    # validate keys
    valid = []
    for k in file_keys:
        if session.query(FileRecord).filter_by(key=k).first():
            valid.append(k)
    if not valid:
        return await message.reply_text("No valid keys provided.")
    group_key = gen_key()
    grp = LinkGroup(key=group_key, file_keys=",".join(valid))
    session.add(grp); session.commit()
    await message.reply_text(f"Group link created: {BASE_URL + group_key}")

# /stats (admin)
@app.on_message(filters.command("stats") & filters.private)
async def stats_command(client: Client, message: Message):
    if message.from_user.id != OWNER_ID:
        return
    # members count
    try:
        info = await client.get_chat(CHANNEL_ID)
        members = info.members_count if hasattr(info, "members_count") else "Unknown"
    except Exception as e:
        members = "Unavailable"
    # total views: iterate stored files and sum views from channel message
    total_views = 0
    rows = session.query(FileRecord).all()
    for r in rows:
        try:
            ch_msg = await client.get_messages(CHANNEL_ID, r.channel_message_id)
            total_views += getattr(ch_msg, "views", 0) or 0
        except:
            pass
    await message.reply_text(f"Channel members: {members}\nTotal stored files: {len(rows)}\nTotal views (sum): {total_views}")

if __name__ == "__main__":
    print("Bot running...")
    app.run()
