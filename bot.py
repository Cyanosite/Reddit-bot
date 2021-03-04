import requests
import time
lastlink = '______________________________'
collection = {}
stocks = {}

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

while True:
    time_atm = time.asctime(time.localtime()).split()
    if 0 < int(time_atm[3][6:8]) < 10:
        tickers = {}
        r = requests.get('http://www.reddit.com/r/wallstreetbets/new.json?limit=50',
                        headers={'User-agent': 'Ticker stats'})
        data = r.json()
        for item in data['data']['children']:
            if item['data']['permalink'] in lastlink:
                break
            item = item['data']['title'].split(' ')
            stocks_temp = []
            for word in item:
                if word[0] == '$':
                    word = word.upper()
                word = word.strip('$,></:"[]}{`()-=+1234567890!?|@#%^&*~§')
                if word in stocks.keys():
                    if word in stocks_temp:
                        continue
                    stocks_temp.append(word)
                    if word not in tickers.keys():
                        tickers[word] = 0
                    tickers[word] += 1

        lastlink = []
        for i, item in enumerate(data['data']['children']):
            lastlink.append(item['data']['permalink'])

        for key, value in tickers.items():
            if key in collection:
                collection[key] += value
            else:
                collection[key] = value

        if int(time_atm[3][3:5]) % 15 == 0:
            with open(f'{time_atm[1]}_{time_atm[2]}.txt', 'a') as document:
                document.write(f'{time.asctime(time.localtime())}\n{collection}\n')
        if int(time_atm[3][0:2]) == 23 and int(time_atm[3][3:5]) == 59:
            with open(f'{time_atm[1]}_{time_atm[2]}.txt', 'a') as document:
                document.write(f'{time_atm[1]} {time_atm[2]} summary:\n')
                for key, value in collection.items():
                    document.write(f'{key} - {stocks[key]}: {value}\n')
            collection = {}
            time.sleep(200)
        time.sleep(45)
    time.sleep(5)
