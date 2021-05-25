from env import env

import requests
import urllib
import pymongo
from datetime import datetime
import pytz


''' PancakeSwap API integrations
    https://github.com/pancakeswap/pancake-info-api/blob/develop/v2-documentation.md
'''


def connectDB():

    username = urllib.parse.quote_plus(env.mongodb_user)
    password = urllib.parse.quote_plus(env.mongodb_pass)

    client = pymongo.MongoClient(f'mongodb://{username}:{password}@{env.mongodb_host}:{env.mongodb_port}')

    db = client[env.mongodb_db]

    return(db)


def query(endpoint: str) -> dict:
    ''' Performs requests query to api
        Returns response as dictionary with timestamp
    '''

    base_url = 'https://api.pancakeswap.info/api/v2/'

    # Remove proceeding '/' if it exists
    if endpoint[0] == '/':
        del endpoint[0]

    # Perform the request and convert to dictionary
    response = requests.get(f'{base_url}{endpoint}')
    response = response.json()

    timestamp = response['updated_at']
    timestamp = int(timestamp) / 1000
    timestamp = datetime.fromtimestamp(timestamp)
    timestamp = timestamp.replace(tzinfo=pytz.timezone(env.tz))

    response['timestamp'] = timestamp

    return(response)



def getTokenInfo(address: str) -> dict:
    ''' Input the token address <str>
        Returns the token information <dict>
        Uses pancakeswap API (unknown limit)
    '''

    url = f"https://api.pancakeswap.info/api/v2/tokens/{address}"

    response = requests.get(url)
    response = response.json()
    
    return(response)


def getTokens(db) -> None:
    '''Returns the tokens in the top ~1000 pairs on PancakeSwap, sorted by reserves.
    '''

    # Get data from API
    endpoint = 'tokens'
    response = query(endpoint)
    data = response['data']
    
    for token, info in data.items():

        info['timestamp'] = response['timestamp']
        info['price'] = float(info['price'])
        info['price_BNB'] = float(info['price_BNB'])
        info['address'] = token

        db['pancakeswap_tokens'].insert_one(info)
    

def getPairs(db: pymongo.MongoClient) -> None:
    '''Gets data for the top ~1000 PancakeSwap pairs, sorted by reserves.
        Inserts in to MongoDB with timestamp
    '''

    # Get data from API
    endpoint = 'pairs'
    response = query(endpoint)
    data = response['data']
    
    for key_pair, info in data.items():

        info['timestamp'] = response['timestamp']

        db['pancakeswap_pairs'].insert_one(info)
    


def getPancakes() -> None:
    ''' Main run loop
    '''

    db = connectDB()
    #getPairs(db)
    getTokens(db)

if __name__ == '__main__':

    getPancakes()


