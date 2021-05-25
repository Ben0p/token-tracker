# BOT Version 01

## Buy / Sell margin back testing scripts

The idea was to back test different stop-loss and buy-stop values, while also considering the trading/swap fee.

Data dumps are in the data folder, the result spreadsheets are in the results folder.

The longer term DAY intervals produce better results. Unsure if this actually applies in the real world.

#### BOT01
- Trash, doesn't work.

#### BOT02
- Manual stop-loss and buy-stop margins

#### BOT03
- Random stop-loss and buy-stop margins
  - Faster, less accurate 

#### BOT04
- Brute-force stop-loss and buy-stop margins to whole percent accuracy
  - Slower, more accurate

#### BOT05
- Brute-force from a specific date with a specific amount, simulate real world position
  - Doesn't really work logically because it performs actions that would not have been done
  - e.g. it might sell 1 day after your buy position but you have held IRL

#### BOT06
- Brute-force to two decimal places
  - Very slow, most accurate
  - Don't use, takes a prohibitively long time