# Good-morning-bot

- sends 'good morning' messages every day
- the token for the bot must be stored in a file "token.txt" in plain text in the same directory as the script
- saves running jobs in a csv file "running_jobs.csv" and restarts them after downtime
- randomized bonus sentences are stored in "novelejumi.txt"

## auto_bot.py

The simpler bot version. The user can start and stop messaging.
When messaging is started, a random time between 7:00 and 7:59 
is generated for that user. The time will stay the same unless
/start command is used again.

## bot.py

The user can set a specified time for messages with
"/set h min"  

Otherwise it is the same.

## Automation

`tmux` is used to run and kill the current bot.

2 cronjobs for making a new session and killing it:

`59 6 * * * tmux new-session -d -s gm_bot "python3 path/to/auto_bot.py"`

`0 8 * * * tmux kill-session -t gm_bot`

The only downside is that the user cannot immediately see the results 
of the commands outside of that time interval. Everything will be
processed at once when the bot script is run again. 
