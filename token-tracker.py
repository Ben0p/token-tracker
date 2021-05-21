from env import env

import time
import json

from queries import bitquery, bscscan, coinspot, forex, pancake, uniswap



def getCoinSpotBalances(key: str, secret: str) -> list:

    balances: list = coinspot.getBalances(key, secret)

    rate: float = forex.getExchangeRate('AUD', 'USD')

    results: list = []

    for balance in balances:
        for coin in balance:

            balance_aud = float(balance[coin]['audbalance'])
            rate_aud = float(balance[coin]['rate'])
            rate_usd = rate_aud * rate

            result = {
                'symbol' : coin,
                'name' : '',
                'balance' : balance[coin]['balance'],
                'rate_usd' : rate_usd,
                'rate_aud' : rate_aud,
                'balance_usd' : balance_aud * rate,
                'balance_aud' : balance_aud
            }

            results.append(result)
    
    return(results)


def getBNBBalance(wallet: str, key: str) -> list:

    address = '0xbb4cdb9cbd36b01bd1cbaebf2de08d9173bc095c'
    rate: float = forex.getExchangeRate('USD', 'AUD')

    bnb_balance = bscscan.getBnbBalance(wallet, key)
    info = pancake.getBSCTokenInfo(address)
    rate_usd = float(info['data']['price'])
    rate_aud = rate_usd * rate
    balance_usd = bnb_balance * rate_usd
    balance_aud = balance_usd * rate

    result = {
            'symbol' : 'WBNB',
            'name' : 'Wrapped BNB',
            'balance' : bnb_balance,
            'rate_usd' : rate_usd,
            'rate_aud' : rate_aud,
            'balance_usd' : balance_usd,
            'balance_aud' : balance_aud
        }
    
    return([result])


def getBSCBalances(wallet: str) -> list:

    rate: float = forex.getExchangeRate('USD', 'AUD')

    results: list = []

    tokens = bitquery.getBSCTokens(wallet)
    
    for token in tokens:
        symbol = token['currency']['symbol']
        name = token['currency']['name']
        balance = float(token['value'])
        address = token['currency']['address']

        try:
            rate_usd = pancake.getBSCTokenInfo(address)
            rate_usd = float(rate_usd['data']['price'])
            rate_aud = rate_usd * rate
            balance_usd = balance * rate_usd
            balance_aud = balance_usd * rate
        except KeyError:
            rate_usd = 0
            rate_aud = 0
            balance_usd = 0
            balance_aud = 0
        
        result = {
            'symbol' : symbol,
            'name' : name,
            'balance' : balance,
            'rate_usd' : rate_usd,
            'rate_aud' : rate_aud,
            'balance_usd' : balance_usd,
            'balance_aud' : balance_aud
        }

        results.append(result)
    
    return(results)


def getETHBalances(wallet: str) -> list:

    rate: float = forex.getExchangeRate('USD', 'AUD')

    results: list = []
        
    tokens = bitquery.getETHTokens(wallet)

    for token in tokens:
        symbol = token['currency']['symbol']
        name = token['currency']['name']
        balance = float(token['value'])
        address = token['currency']['address']

        try:
            rate_usd = uniswap.getTokenValue(address)
            rate_aud = rate_usd * rate
            balance_usd = balance * rate_usd
            balance_aud = balance_usd * rate
        except KeyError:
            rate_usd = 0
            rate_aud = 0
            balance_usd = 0
            balance_aud = 0
        
        result = {
            'symbol' : symbol,
            'name' : name,
            'balance' : balance,
            'rate_usd' : rate_usd,
            'rate_aud' : rate_aud,
            'balance_usd' : balance_usd,
            'balance_aud' : balance_aud
        }

        results.append(result)
    
    return(results)


def run():
    
    total_aud = 0

    print("Retrieving CoinSpot balances...")
    coinspot_balances = getCoinSpotBalances(env.coinspot_key, env.coinspot_secret)
    print("Retrieving BNB balance...")
    bnb_balance = getBNBBalance(env.bsc_wallet, env.bscscan_key)
    print("Retrieving BSC balances...")
    bsc_balances = getBSCBalances(env.bsc_wallet)
    print("Retrieving ETH balances...")
    eth_balances = getETHBalances(env.bsc_wallet)
    
    print(eth_balances)

    balances = coinspot_balances + bnb_balance + bsc_balances + eth_balances

    for balance in balances:

        total_aud += balance['balance_aud']

        print(f"{balance['symbol']}:")
        print(f"     Balance: {balance['balance']}")
        print(f"    Rate AUD: ${balance['rate_aud']}")
        print(f" Balance AUD: ${balance['balance_aud']}")
        print("="*50)
    print("_"*50)
    print(f'   Total AUD: ${total_aud}')




if __name__ == "__main__":

    run()