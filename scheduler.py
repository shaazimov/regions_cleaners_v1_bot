import json
from datetime import datetime, time as dtime
import pytz
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram import Bot
from dateutil.parser import parse as date_parse

def load():
    with open("data.json", "r") as f:
        data = json.load(f)
    with open("config.json", "r") as f:
        config = json.load(f)
    return data, config

def save(data):
    with open("data.json", "w") as f:
        json.dump(data, f, indent=4)

def start_scheduler(bot: Bot):
    data, config = load()
    tz = pytz.timezone(config["timezone"])
    scheduler = AsyncIOScheduler(timezone=tz)
    
    @scheduler.scheduled_job("cron", hour=0, minute=0)
    async def daily_check():
        data, config = load()
        today = datetime.now(tz).date()
        due_regions = []

        for region in data["regions"]:
            new_dates = []
            for d in region["dates"]:
                dt = date_parse(d).date()
                if dt == today:
                    due_regions.append(region)
                else:
                    new_dates.append(d)
            region["dates"] = new_dates

        save(data)

        if not due_regions:
            return
        
        combined_time = {}
        for r in due_regions:
            t = r.get("time", config["default_reminder_time"])
            combined_time.setdefault(t, []).append(r["name"])

        for t, names in combined_time.items():
            hh, mm = map(int, t.split(":"))
            scheduler.add_job(send_reminder, "cron", hour=hh, minute=mm, args=[bot, names])

    async def send_reminder(bot: Bot, names):
        _, config = load()
        text = "📞 **Reminder**\nCall today:\n- " + "\n- ".join(names)

        for uid in config["allowed_users"]:
            await bot.send_message(uid, text, parse_mode="Markdown")

    scheduler.start()
