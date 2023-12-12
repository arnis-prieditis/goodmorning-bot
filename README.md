# Good-morning-bot

- sends 'good morning' messages every day at the user specified time
- the token for the bot must be stored in a file "token.txt" in plain text in the same directory as the script
- saves running jobs in a csv file "running_jobs.csv" and restarts them after downtime

## current pros

- the user can control the time of the message and cancel/re-enable messaging at any moment
- can work for multiple users at once

## current cons

- probably more resource intensive

## alternative 1

Make a script that sends one randomized message.

Set up a cron job for that script.

The downside of that approach is that I have to manually set up the
target user's ID and messaging time. And the user has no control 
over the bot.

## alternative 2

Use `tmux` to run and kill the current bot.

Set up 2 cronjobs for making a new session and killing it (e.g. one at 05:00, one at 12:00)

The only downside would be that the user cannot immediately see the results 
of set and unset commands outside of that time interval. Everything will be
processed at once when the bot script is run again. 

## TODO 

- randomize messages with novēlējumi or inspirational quotes
- make so that the bot adapts to the user's local time zone (for current variant)
- talk to target user about the best bot version
