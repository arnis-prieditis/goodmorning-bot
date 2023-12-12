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

# set the time zone for messages
riga = timezone("Europe/Riga")

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# Get bot token
TOKEN = ""
with open("token.txt", "r") as token_file:
    TOKEN = token_file.readline()
    TOKEN.strip()

path_to_csv = "running_jobs.csv"

# Define a few command handlers.
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends explanation on how to use the bot."""
    await update.message.reply_text("Hi! Use /set <hour> <minute> to set a time for the messages.\nUse /unset to stop the messages.")


async def alarm(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send the alarm message."""
    job = context.job
    await context.bot.send_message(job.chat_id, text=f"Beep! Good morning, {job.data}!")


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


async def set_message_time(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Add a job to the queue."""
    chat_id = update.effective_message.chat_id
    try:
        # args[0] should contain the hours for the message
        # args[1] should contain the minutes
        hour = int(context.args[0])
        minute = int(context.args[1])
        if hour < 0 or minute < 0:
            await update.effective_message.reply_text("Sorry, but we can not bend time!")
            return

        t = time(hour, minute, 0, tzinfo=riga)
        t_upper = time(12, 0, 0)
        t_lower = time(5, 0, 0)
        if t > t_upper or t < t_lower:
            await update.effective_message.reply_text("Sorry, but those aren't my morning hours. Please, set a time between 5:00 and 12:00")
            return

        job_removed = remove_job_if_exists(str(chat_id), context)

        first_name = update.effective_message.chat.first_name
        context.job_queue.run_daily(alarm, time=t, chat_id=chat_id, name=str(chat_id), data=first_name)

        new_row = [chat_id, first_name, t]
        with open(path_to_csv, "a", newline="") as running_jobs_file:
            csv_writer = csv.writer(running_jobs_file)
            csv_writer.writerow(new_row)

        text = "Time successfully set!"
        if job_removed:
            text += " Old schedule was removed."
        await update.effective_message.reply_text(text)

    except (IndexError, ValueError):
        await update.effective_message.reply_text("Usage: /set <hour> <minute>")


async def unset(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Remove the job if the user changed their mind."""
    chat_id = update.message.chat_id
    job_removed = remove_job_if_exists(str(chat_id), context)
    text = "Messages successfully cancelled!" if job_removed else "You have not set a time for messages."
    await update.message.reply_text(text)


def main() -> None:
    """Run bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(TOKEN).build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler(["start", "help"], start))
    application.add_handler(CommandHandler("set", set_message_time))
    application.add_handler(CommandHandler("unset", unset))

    # continue the previously set jobs
    with open(path_to_csv, "r") as running_jobs_file:
        csv_reader = csv.reader(running_jobs_file)
        for row in csv_reader:
            chat_id = row[0]
            first_name = row[1]
            time_digits = list(map(lambda x : int(x), row[2].split(":")))
            t = time(time_digits[0], time_digits[1], 0, tzinfo=riga)
            application.job_queue.run_daily(alarm, time=t, chat_id=chat_id, name=str(chat_id), data=first_name)

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()