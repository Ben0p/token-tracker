from typing import Tuple
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
    Performs some coinspot API requests and returns the responses
'''


def connectDB():

    username = urllib.parse.quote_plus(env.mongodb_user)
    password = urllib.parse.quote_plus(env.mongodb_pass)

    client = pymongo.MongoClient(f'mongodb://{username}:{password}@{env.mongodb_host}:{env.mongodb_port}')

    db = client[env.mongodb_db]

    return(db)


def query(path: str, data: dict = False) -> list:
    ''' Creates, signs and posts the API request
        Returns dictionary response
    '''

    # Convert secret to bytes
    secret = env.coinspot_secret.encode('utf-8')

    # Construct the nonce
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

    # Coinspot url
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
    response_data = json.loads(response_data)

    # Append timestamp
    timestamp = datetime.now()
    timestamp = timestamp.replace(tzinfo=pytz.timezone(env.tz))
    response_data['timestamp'] = timestamp

    # Close connection
    conn.close()

    return(response_data)



def getBalances(db: pymongo.MongoClient) -> Tuple:
    ''' Gets the CoinSpot balances (using the query function)
        Updates MongoDB with time stamps
    '''
    
    path = '/api/v2/ro/my/balances'
    response = query(path)


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
        return(True, response['message'])

    else:
        return(False, response['message'])


def buyQuotes(db: pymongo.MongoClient) -> None:

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
            #print(f"{coin['symbol']}: ${response['rate']}")
    
  
def sellQuotes(db: pymongo.MongoClient) -> None:

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


def swapQuotes(db: pymongo.MongoClient) -> None:

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




if __name__ == "__main__":

    db = connectDB()
    #buyQuotes(db)
    #sellQuotes(db)
    #calcSplit(db)
    swapQuotes(db)

    '''
    while True:

        db = connectDB()

        while True:
            try:
                ############
                # Balances #
                ############
                success, message = getBalances(db)
                if success:
                    print(f'Retrieved CoinSpot balances ({message})')
                else:
                    print(f'Error retriving CoinSpot balances ({message})')
            
                time.sleep(env.interval)
            except pymongo.errors.ServerSelectionTimeoutError:
                print("Lost connection to MongoDB")
                break
    '''