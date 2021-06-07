import numpy as np



''' This script does multiple sweeps at different accuracies
    First Sweep: Whole decimal points 0 - 100 %
    Second Sweep: One decimal point +- 10% of previous result
    Third Sweep: Two decimal points +- 5% of precious result
'''



def getData(file: str)-> list:

    with open(file, 'r') as f:
        l = list(f)
        f.close()
    
    return(l)


def backtest(l: list, buy_range: list, sell_range: list, record_balance: float) -> dict:

    swap_fee = 1 # Swap fee percent

    for buy_margin in buy_range:
        for sell_margin in sell_range:
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

                result = {
                    'final_balance' : record_balance,
                    'sell_margin' : sell_margin,
                    'buy_margin' : buy_margin
                }

    return(result)


def test(file):

    l = getData(file)

    ###############
    # First Sweep #
    ###############

    print("STARTING FIRST SWEEP:")

    # Generate range to iterate over, whole percentages
    interval = np.arange(0,100)

    result = backtest(l, interval, interval, 0)

    print("FIRST SWEEP RESULTS:")
    print(result)

    ################
    # Second Sweep #
    ################

    print("STARTING SECOND SWEEP:")

    buy_range = np.linspace(
        result['buy_margin'] - 15,
        result['buy_margin'] + 15,
        200
    )

    sell_range = np.linspace(
        result['sell_margin'] - 15,
        result['sell_margin'] + 15,
        200
    )

    try:
        result = backtest(l, buy_range, sell_range, result['final_balance'])

        print("SECOND SWEEP RESULTS:")
        print(result)
    except:
        print("No improvement")

    ###############
    # Third Sweep #
    ###############

    print("STARTING THIRD SWEEP:")

    buy_range = np.linspace(
        result['buy_margin'] - 1,
        result['buy_margin'] + 1,
        200
    )

    sell_range = np.linspace(
        result['sell_margin'] - 1,
        result['sell_margin'] + 1,
        200
    )

    try:
        result = backtest(l, buy_range, sell_range, result['final_balance'])

        print("THIRD SWEEP RESULTS:")
        print(result)
    except:
        print("No improvement")


if __name__ == "__main__":

    file = 'data\Binance_BTCUSDT_d.csv'
    test(file)