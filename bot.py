import requests
import time
# stores all the link from last request
lastlink = []
# initial ticker names from the txts
stocks = {}
# daily summary, updates value every 15 minutes
collection = {}
# 15 min summary, updates value every minute
summary = {}

# importing ticker names from the files. ('ticker\tcompany')
with open('NASDAQ.txt') as nasdaq:
    nasdaq.readline()
    for line in nasdaq:
        line = line.strip().split('\t')
        stocks[line[0]] = line[1]
with open('NYSE.txt') as nyse:
    nyse.readline()
    for line in nyse:
        line = line.strip().split('\t')
        stocks[line[0]] = line[1]

# making an infinite loop
while True:
    # get current time at the start of the loop
    time_atm = time.asctime(time.localtime()).split()
    # if seconds are between 0 and 10
    if 0 < int(time_atm[3][6:8]) < 10:
        tickers = {}
        # GET last 100 posts from r/wallstreetbets while sort = new
        r = requests.get('http://www.reddit.com/r/wallstreetbets/new.json?limit=100')
        # put data into json
        data = r.json()
        for item in data['data']['children']:
            # if the post's permanent link was present in the last request then it
            # breaks the loop so it won't get more tickers
            if item['data']['permalink'] in lastlink:
                break
            # splits title into words
            item = item['data']['title'].split(' ')
            # temporarily stores the tickers that we already recorded in the tickers list
            stocks_temp = []
            for word in item:
                # if the somene doesn't put the ticker in all capitals but still has the $
                # sign indicating that it's a ticker we make it uppercase
                if word[0] == '$':
                    word = word.upper()
                # get rid of unnecessary characters, because sometimes people put it at the end of the line or something
                word = word.strip('$,></:"[]}{`()-=+1234567890!?|@#%^&*~§')
                # if the word is a ticker (present in the stocks list that we read from the txts)
                if word in stocks.keys():
                    # if this title already had the exact same ticker then this ensures it will only get added once
                    if word in stocks_temp:
                        continue
                    # adds the ticker into the found tickers in the current title
                    # I used this method because if I break the loop after the first found ticker
                    # it wouldn't record other tickers that are different
                    stocks_temp.append(word)
                    if word not in tickers.keys():
                        tickers[word] = 0
                    tickers[word] += 1

        # we get the last links, it's important to get every single one to avoid errors, because the new request
        # may not contain certain posts that have been removed since the last request and in that case it would record some tickers again
        lastlink = []
        for item in data['data']['children']:
            lastlink.append(item['data']['permalink'])

        # adding our tickers to the summary, which is important for recording all the new tickers in the last 15 minutes
        for key, value in tickers.items():
            if key in summary:
                summary[key] += value
            else:
                summary[key] = value

        # every 15 minutes
        if int(time_atm[3][3:5]) % 15 == 0:
            # open a txt with today's date
            with open(f'{time_atm[1]}_{time_atm[2]}.txt', 'a') as document:
                # sorting summaries by their value descending
                summary = {k: v for k, v in sorted(summary.items(), key=lambda item: item[1], reverse=True)}
                document.write(f'{time.asctime(time.localtime())}\n')
                for i in summary:
                    document.write(f'{i} - {summary[i]}\n')
            summary = {}
            # adding our summary to the collection, important for daily summary
            for key, value in tickers.items():
                if key in collection:
                    collection[key] += value
                else:
                    collection[key] = value

        # at 23:59 every day (last run of the day), same procedure with summary
        if int(time_atm[3][0:2]) == 23 and int(time_atm[3][3:5]) == 59:
            with open(f'{time_atm[1]}_{time_atm[2]}.txt', 'a') as document:
                collection = {k: v for k, v in sorted(collection.items(), key=lambda item: item[1], reverse=True)}
                document.write(f'{time_atm[1]} {time_atm[2]} summary:\n')
                for i in collection:
                    document.write(f'{i} - {stocks[i]}: {collection[i]}\n')
            collection = {}
        # sleep for more than 10 so it won't run again in the same minute
        time.sleep(45)
    # sleep 5 seconds, so it will always land in the 0 < time < 10 interval, so it'll run every minute
    time.sleep(5)
