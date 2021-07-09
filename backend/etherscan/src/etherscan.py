from env import env

import requests
import pymongo
import urllib
import time
import json



def connectDB() -> pymongo.MongoClient:
    ''' Connects to a pymongo DB (specified in the env)
        Returns the MongoClient connection object
    '''

    username = urllib.parse.quote_plus(env.mongodb_user)
    password = urllib.parse.quote_plus(env.mongodb_pass)

    client = pymongo.MongoClient(f'mongodb://{username}:{password}@{env.mongodb_host}:{env.mongodb_port}')

    db = client[env.mongodb_db]

    return(db)


def get_eth_tokens(DB: pymongo.MongoClient) -> list:
    '''Gets token list from database'''

    eth_tokens = DB['eth_tokens'].find()

    return(eth_tokens)


def get_abi(
    api_key: str,
    token_address: str
    ):
    '''Gets ABI of a token contract'''

    request = f"https://api.etherscan.io/api?module=contract&action=getabi&address={token_address}&apikey={api_key}"

    response = requests.get(request)
    response = response.json()
    
    return(response)


def save_abi(
    db: pymongo.MongoClient,
    abi: str,
    address: str
    ) -> None:
    '''Saves token abi to db'''

    db['eth_tokens'].find_one_and_update(
        {
            'address' : address
        },
        {
            '$set' : {
                'abi' : abi
            }
        }
    )


def run():
    ''' 
    ''' 

    while True:

        db = connectDB()

        while True:

            eth_tokens = get_eth_tokens(db)
            for token in eth_tokens:
                if 'abi' not in token and token['address'] != '-':
                    abi = get_abi(env.etherscan_key, token['address'])
                    if abi['message'] == 'OK':
                        save_abi(db, abi['result'], token['address'])
                        print(f"Retrived {token['symbol']} contract ABI")
            

            print(f"Sleep {env.interval} seconds")
            time.sleep(env.interval)



if __name__ == "__main__":

    run()