#!/usr/bin/python3
#/usr/local/bin/

from env import env

import hmac
import hashlib
import time
import json
import http.client as httplib
import pymongo
import urllib
from datetime import datetime
import pytz



'''
    Performs coinspot API requests and returns the responses
'''


def connectDB() -> pymongo.MongoClient:
    ''' Connects to a pymongo DB (specified in the env)
        Returns the MongoClient connection object
    '''

    username = urllib.parse.quote_plus(env.mongodb_user)
    password = urllib.parse.quote_plus(env.mongodb_pass)

    client = pymongo.MongoClient(f'mongodb://{username}:{password}@{env.mongodb_host}:{env.mongodb_port}')

    db = client[env.mongodb_db]

    return(db)


def query(path: str, data: dict = False) -> list:
    ''' Creates, signs and posts the API request
        Returns dictionary response
        path: The api endpoint path
        data: A Dictionary of the data to POST
    '''

    # Convert secret to bytes (from the env file)
    secret = env.coinspot_secret.encode('utf-8')

    # Construct the nonce (unix time)
    nonce = int(time.time()*1000000)
    postdata = {
        'nonce' :  nonce
    }

    if data:
        for key, value in data.items():
            postdata[key] = value

    # Convert parameters to json
    params = json.dumps(postdata, separators=(',', ':'))

    # Sign the message with the secret using sha512
    signedMessage = hmac.new(secret, params.encode('utf-8'), hashlib.sha512).hexdigest()

    # Construct the headers
    headers = {}
    headers['Content-type'] = 'application/json'
    headers['Accept'] = 'text/plain'
    headers['key'] = env.coinspot_key
    headers['sign'] = signedMessage

    # Coinspot base url
    endpoint = "www.coinspot.com.au"

    # Create connection
    conn = httplib.HTTPSConnection(endpoint)

    # Perform the POST
    conn.request("POST", path, params, headers)
    response = conn.getresponse()

    #print response.status, response.reason
    response_data = response.read()

    # Decode and convert json to dict then get the balances list
    response_data = response_data.decode("utf-8")
    try:
        response_data = json.loads(response_data)
    except json.decoder.JSONDecodeError:
        response_data = {
            'status' : None
        }

    # Append timestamp
    timestamp = datetime.now()
    timestamp = timestamp.replace(tzinfo=pytz.timezone(env.tz))
    response_data['timestamp'] = timestamp

    # Close connection
    conn.close()

    return(response_data)


def getBalances(db: pymongo.MongoClient) -> tuple:
    ''' Gets the CoinSpot balances (using the query function)
        Updates MongoDB with time stamps
    '''

    print('############')
    print('# Balances #')
    print('############')
    
    path = '/api/v2/ro/my/balances'
    response = query(path)
    total = 0

    if response['status'] == 'ok':
        for balance in response['balances']:
            for key in balance:
                db['coinspot_balances'].insert_one(
                    {
                        'symbol' : key,
                        'timestamp' : response['timestamp'],
                        'balance' : balance[key]['balance'],
                        'audbalance' : balance[key]['audbalance'],
                        'rate' : balance[key]['rate'],             
                    },
                )
            total += balance[key]['balance']
            print(f"{key}: ${balance[key]['audbalance']}")


def buyQuotes(db: pymongo.MongoClient) -> None:
    ''' Get quote for $AUD for each coin in DB
    ''' 

    print('##############')
    print('# Buy Quotes #')
    print('##############')

    coins = db['coinspot_coins'].find()

    path = '/api/v2/quote/buy/now'

    for coin in coins:
        data = {
            'cointype' : f"{coin['symbol']}",
            'amount' : '1',
            'amounttype' : 'aud'
        }

        response = query(path, data)

        if response['message'] == 'ok':
            db['coinspot_buy'].insert_one(
                {
                    'coin_id' : coin['_id'],
                    'timestamp' : response['timestamp'],
                    'rate' : response['rate']
                }
            )
            print(f"{coin['symbol']}: ${response['rate']}")
    
  
def sellQuotes(db: pymongo.MongoClient) -> None:

    print('###############')
    print('# Sell Quotes #')
    print('###############')

    coins = db['coinspot_coins'].find()

    path = '/api/v2/quote/sell/now'

    for coin in coins:
        data = {
            'cointype' : f"{coin['symbol']}",
            'amount' : '1',
            'amounttype' : 'aud'
        }

        response = query(path, data)
        if response['message'] == 'ok':
            db['coinspot_sell'].insert_one(
                {
                    'coin_id' : coin['_id'],
                    'timestamp' : response['timestamp'],
                    'rate' : response['rate']
                }
            )

            print(f"{coin['symbol']}: ${response['rate']}")


def swapQuotes(db: pymongo.MongoClient) -> None:
    ''' Get swap quotes to USDT for coins in DB
    '''

    print('###############')
    print('# Swap Quotes #')
    print('###############')

    coins = db['coinspot_coins'].find()

    path = '/api/v2/quote/swap/now'

    for coin in coins:
        data = {
            'cointypesell' : 'USDT',
            'cointypebuy' : coin['symbol'],
            'amount' : 1
        }

        response = query(path, data)
        if response['message'] == 'ok':
            db['coinspot_swap'].insert_one(
                {
                    'coin_id' : coin['_id'],
                    'timestamp' : response['timestamp'],
                    'rate' : response['rate']
                }
            )

            print(f"{coin['symbol']}:USDT - {response['rate']}")


def calcSplit(db: pymongo.MongoClient) -> None:
    ''' Calculates the difference between buy and  sell price
    '''

    print('##########')
    print('# Splits #')
    print('##########')

    coins = db['coinspot_coins'].find()

    for coin in coins:

        buy = db['coinspot_buy'].find_one(
            {
                'coin_id' : coin['_id']
            },
            sort=[( 'timestamp', pymongo.DESCENDING )]
        )

        sell = db['coinspot_sell'].find_one(
            {
                'coin_id' : coin['_id']
            },
            sort=[( 'timestamp', pymongo.DESCENDING )]
        )

        split = ((buy['rate'] - sell['rate']) / ((buy['rate'] + sell['rate'])/2)) * 100
        split = round(split, 2)
        
        split_aud = buy['rate'] - sell['rate']
        split_aud = round(split_aud, 2)
 
        print(f"{coin['symbol']} split: {split}% (${split_aud})")


def run():
    ''' Main run loop
    '''

    while True:

        db = connectDB()

        while True:
            try:
                getBalances(db)
                buyQuotes(db)
                sellQuotes(db)
                swapQuotes(db)
                calcSplit(db)
            
                print(f"Done, sleeping {env.interval} seconds.")
                time.sleep(env.interval)
            except pymongo.errors.ServerSelectionTimeoutError:
                print("Lost connection to MongoDB")
                break


if __name__ == "__main__":

    run()
