import random


swap_fee = 1 # Swap fee percent


with open('Binance_BNBUSDT_minute.csv', 'r') as f:
    l = list(f)
    f.close()


track = []

buy_margin =  7 # Percent increase to re-buy
sell_margin =  7 # Percent drop to sell

start_amount = 100
bank = 0
balance = 0
holding = True


for idx, line in enumerate(l[1:]):

    line = line.strip()
    line = line.split(',')
    market_close = float(line[6])

    new_stop_loss = market_close * (1-(sell_margin/100))
    new_buy_stop =  market_close * (1+(buy_margin/100))

    if idx == 0:
        stop_loss = new_stop_loss
        buy_stop = new_buy_stop
        prev_close = market_close
        position = start_amount
        continue
    
    change = (market_close - prev_close) / prev_close
    prev_close = market_close
    
    if holding:
        position = position + (position * change)
        buy_stop = new_buy_stop

        if market_close <= stop_loss:
            holding = False
            position = position * (1-(swap_fee/100))
            bank = position
            position = 0
        else:
            if new_stop_loss > stop_loss:
                stop_loss = new_stop_loss

    if not holding:

        stop_loss = new_stop_loss

        if market_close >= buy_stop:
            holding = True
            position = bank
            position = position * (1-(swap_fee/100))
            bank = 0
        else:
            if new_buy_stop < buy_stop:
                buy_stop = new_buy_stop

    balance = position + bank
    track.append((line[1], market_close, stop_loss, buy_stop, balance))


with open("track.csv", 'w') as t:
    t.write("date,market_close,stop_loss,buy_stop, balance\n")  
    for row in track:
        t.write(f"{row[0]},{row[1]},{row[2]},{row[3]}, {row[4]}\n")
    t.close()