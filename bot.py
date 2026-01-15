import json
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from scheduler import start_scheduler
import asyncio
import os

logging.basicConfig(level=logging.INFO)

TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher()

def load_config():
    with open("config.json", "r") as f:
        return json.load(f)

@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    await message.answer("Bot running. You will receive reminders if permitted.")

@dp.message(Command("listusers"))
async def list_users(message: types.Message):
    config = load_config()
    text = "Allowed users:\n" + "\n".join(str(u) for u in config["allowed_users"])
    await message.answer(text)

@dp.message(Command("adduser"))
async def add_user(message: types.Message):
    config = load_config()
    parts = message.text.split()

    if len(parts) != 2:
        await message.answer("Usage: /adduser <user_id>")
        return

    uid = int(parts[1])
    if uid not in config["allowed_users"]:
        config["allowed_users"].append(uid)
        with open("config.json", "w") as f:
            json.dump(config, f, indent=4)
        await message.answer(f"User {uid} added.")
    else:
        await message.answer("User already exists.")

@dp.message(Command("removeuser"))
async def remove_user(message: types.Message):
    config = load_config()
    parts = message.text.split()

    if len(parts) != 2:
        await message.answer("Usage: /removeuser <user_id>")
        return

    uid = int(parts[1])
    if uid in config["allowed_users"]:
        config["allowed_users"].remove(uid)
        with open("config.json", "w") as f:
            json.dump(config, f, indent=4)
        await message.answer(f"User {uid} removed.")
    else:
        await message.answer("User not found.")

async def main():
    start_scheduler(bot)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
