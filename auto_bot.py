#!/usr/bin/env python

"""
Simple Bot to send "good morning" messages at the specified time.
"""

import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from datetime import time
from pytz import timezone
import csv
import random
import os

proj_dir = os.path.dirname(os.path.abspath(__file__))

# set the time zone for messages
riga = timezone("Europe/Riga")

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# Get bot token
TOKEN = ""
path_to_token = proj_dir + "/token.txt"
with open(path_to_token, "r") as token_file:
    TOKEN = token_file.readline()
    TOKEN.strip()

path_to_csv = proj_dir + "/running_jobs.csv"

novelejumi = []
path_to_novelejumi = proj_dir + "/novelejumi.txt"
with open(path_to_novelejumi, "r") as novelejumi_file:
    for row in novelejumi_file:
        novelejumi.append(row)

# Define a few command handlers.
async def help_func(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends explanation on how to use the bot."""
    await update.message.reply_text("Hi! Use /stop to stop my messages.\nUse /start to re-enable them.")


async def alarm(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send the alarm message."""
    job = context.job
    who = (random.choices([job.data, "sweetheart"], weights=[25,1]))[0]
    bonus_sentence = (random.choices(novelejumi))[0]
    await context.bot.send_message(job.chat_id, text=f"Good morning, {who}! {bonus_sentence}")


def remove_job_if_exists(name: str, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Remove job with given name. Returns whether job was removed."""
    current_jobs = context.job_queue.get_jobs_by_name(name)
    if not current_jobs:
        return False
    for job in current_jobs:
        job.schedule_removal()
    new_rows = []
    with open(path_to_csv, "r") as running_jobs_file:
        csv_reader = csv.reader(running_jobs_file)
        for row in csv_reader:
            if row[0] != name:
                new_rows.append(row)
    with open(path_to_csv, "w", newline="") as running_jobs_file:
        csv_writer = csv.writer(running_jobs_file)
        csv_writer.writerows(new_rows)
    return True


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Add a job to the queue."""
    chat_id = update.effective_message.chat_id
    try:
        first_name = update.effective_message.chat.first_name
        job_removed = remove_job_if_exists(str(chat_id), context)

        # will pick a random time between 7:00 and 7:59
        minute = random.randint(0, 59)
        t = time(7, minute, 0, tzinfo=riga)
        context.job_queue.run_daily(alarm, time=t, chat_id=chat_id, name=str(chat_id), data=first_name)

        new_row = [chat_id, first_name, t]
        with open(path_to_csv, "a", newline="") as running_jobs_file:
            csv_writer = csv.writer(running_jobs_file)
            csv_writer.writerow(new_row)

        text = "OK, you'll hear from me soon 😁" if not job_removed else "Was already planning on that. But I can schedule a different time for some intrigue."
        await update.effective_message.reply_text(text)

    except (IndexError, ValueError):
        await update.effective_message.reply_text("Just write \"/start\"")


async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Remove the job if the user changed their mind."""
    chat_id = update.message.chat_id
    job_removed = remove_job_if_exists(str(chat_id), context)
    text = "Messages successfully cancelled!" if job_removed else "I wasn't gonna message you anyway."
    await update.message.reply_text(text)


def main() -> None:
    """Run bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(TOKEN).build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("stop", stop))
    application.add_handler(CommandHandler("help", help_func))

    # continue the previously set jobs
    with open(path_to_csv, "r") as running_jobs_file:
        csv_reader = csv.reader(running_jobs_file)
        for row in csv_reader:
            chat_id = row[0]
            first_name = row[1]
            time_digits = list(map(lambda x : int(x), row[2].split(":")))
            t = time(time_digits[0], time_digits[1], time_digits[2], tzinfo=riga)
            application.job_queue.run_daily(alarm, time=t, chat_id=chat_id, name=str(chat_id), data=first_name)

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()