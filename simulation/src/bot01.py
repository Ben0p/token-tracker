

import time
import random




with open('Binance_BNBUSDT_minute.csv', 'r') as f:

    swap_fee = 1 # Swap fee percent

    f = list(f)

    balance = 0

    while True:

        buy_margin = random.uniform(0.1, 10)
        sell_margin = random.uniform(0.1, 10)
        
        bank = 0 # Bank balance.
        brought = 24.9849 # Initial brought amount
        holding = True # If currently holding

        tracker = []

        for idx, line in enumerate(f[1:]):

            line = line.strip()
            line = line.split(',')
            market_close = float(line[6])

            if idx == 0:
                position = brought
                stop_loss = market_close * (1-(sell_margin/100))
                buy_stop =  market_close * (1+(buy_margin/100))
                prev_close = market_close
                continue

            change = (market_close - prev_close) / prev_close

            if holding:
                position = position + (position * change)
                new_stop_loss = market_close * (1-(sell_margin/100))

                if new_stop_loss > stop_loss:
                    stop_loss = new_stop_loss
                
                if position <= stop_loss:
                    position = position * (1-(swap_fee/100)) # Account for swap fee
                    bank = position
                    position = 0
                    sold = market_close
                    holding = False
            
            if not holding:
                    
                new_buy_stop = market_close * (1+(buy_margin/100))

                if new_buy_stop <= buy_stop:
                    buy_stop = new_buy_stop

                if market_close >= buy_stop:
                    position = position * (1-(swap_fee/100)) # Account for swap fee
                    position = bank
                    bank = 0
                    holding = True
            
            prev_close = market_close

            tracker.append((line[1], market_close, stop_loss, buy_stop,position,bank))

        new_balance = position + bank

        if new_balance > balance:
            balance = new_balance
            gain = (balance / brought) * 100
            print(f"New max: {buy_margin}%/{sell_margin}% - {round(balance,2)}")

            with open("ratio.txt", 'w') as o:
                o.write(f"Buy Margin: {buy_margin}\n")
                o.write(f"Sell Margin: {sell_margin}\n")
                o.write(f"Start: ${brought}\n")
                o.write(f"End: ${balance}\n")
                o.close
            
            with open("track.csv", 'w') as t:
                t.write("date,market_close,stop_loss,buy_stop,position,bank\n")
                for row in tracker:
                    t.write(f"{row[0]},{row[1]},{row[2]},{row[3]}, {row[4]}, {row[5]}\n")
                t.close()

        print(f"{round(buy_margin,2)}%/{round(sell_margin,2)}% - {round(new_balance,2)}")
        