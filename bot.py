import yfinance as yf
import requests
import time
# stores all the links from last request
lastlink = []
# initial ticker names from the txts
stocks = {}
# used to collect new information, and to display the hourly change
tickers = {}
# total mentions
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
        # GET last 100 posts from r/wallstreetbets while sort = new
        r = requests.get('http://www.reddit.com/r/wallstreetbets/new.json?limit=100', headers={'User-agent': 'Ticker stats'})
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

        # every hour
        if int(time_atm[3][3:5]) == 59:
            # putting tickers into summary, as tickers will be used to display the hourly change
            for k, v in tickers.items():
                if k not in summary:
                    summary[k] = v
                else:
                    summary[k] += v
            # sorting summary by their value descending
            summary = {k: v for k, v in sorted(summary.items(), key=lambda item: item[1], reverse=True)}

            with open(f'{time_atm[1]}_{time_atm[2]}.txt', 'a') as document:
                document.write(f'{time_atm[1:]} summary:\n')
                # Detailing every company present in our tickers dictionary
                for i in summary:
                    if summary[i] > 3:
                        # ticker - company name - number of mentions - change in the last hour
                        document.write(f'{i} - {stocks[i]} - {summary[i]} - +{tickers[i]}:\n')
                        # getting the current day's data from the yfinance module
                        info = yf.Ticker(i).history(period='1d')
                        # opening price; closing price
                        document.write(f"opening: {round(info['Open'][0],2)}; current/closing: {round(info['Close'][0],2)}; ")
                        # calculating the stock price change from opening to closing in % rounded to 2 decimals
                        change = round(((info['Close'][0]/info['Open'][0])-1)*100,2)
                        # change%; highest price during the day; lowest price during the day
                        document.write(f"change: {change}%; high: {round(info['High'][0],2)}; low: {round(info['Low'][0],2)}\n")
                document.write("\n\n\n")
        # sleep for more than 10 so it won't run again in the same minute
        time.sleep(45)
    # sleep 5 seconds, so it will always land in the 0 < time < 10 interval, so it'll run every minute
    time.sleep(5)
