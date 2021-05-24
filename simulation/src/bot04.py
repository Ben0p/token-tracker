import random


swap_fee = 1 # Swap fee percent


with open('Binance_BTCUSDT_minute.csv', 'r') as f:
    l = list(f)
    f.close()

    record_balance = 0

for buy_margin in range(0,100):
    for sell_margin in range(0,100):
        track = []

        bank = 0
        holding = True

        for idx, line in enumerate(l[1:]):

            line = line.strip()
            line = line.split(',')
            market_close = float(line[6])

            new_stop_loss = market_close * (1-(sell_margin/100))
            new_buy_stop =  market_close * (1+(buy_margin/100))

            if idx == 0:
                position = market_close
                stop_loss = new_stop_loss
                buy_stop = new_buy_stop
                prev_close = market_close
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

        final_balance = balance

        if final_balance > record_balance:
            record_balance = final_balance
            print(f"New record:")
            print(f"  Final Balance: ${round(final_balance,2)}")
            print(f"    Sell margin: {round(sell_margin,2)}%")
            print(f"     Buy margin: {round(buy_margin,2)}%")
            

            with open("track.csv", 'w') as t:
                t.write("date,market_close,stop_loss,buy_stop, balance\n")  
                for row in track:
                    t.write(f"{row[0]},{row[1]},{row[2]},{row[3]}, {row[4]}\n")
                t.close()