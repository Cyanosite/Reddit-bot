# Reddit-bot
Tracks ticker names in r/wallstreetbets and makes a summary (tickers from nasdaq and nyse txt)

Requests the 100 last new posts on r/wallstreetbest every minute;
every 15 minutes it creates a summary of the tickers that were added in the last 15 minutes,
at the end of every day it makes a summary of that day and starts a new one.

Gets ticker names from the nasdaq and nyse txt and has some additional functionality to avoid some false positives.
