#!/usr/bin/python3
#/usr/local/bin/

import time

from env import env

import urllib
import pymongo
import requests
import json
import datetime
import pytz
import dateutil.parser



def connectDB() -> pymongo.MongoClient:
    ''' Connects to a pymongo DB (specified in the env)
        Returns the MongoClient connection object
    '''

    username = urllib.parse.quote_plus(env.mongodb_user)
    password = urllib.parse.quote_plus(env.mongodb_pass)

    client = pymongo.MongoClient(f'mongodb://{username}:{password}@{env.mongodb_host}:{env.mongodb_port}')

    db = client[env.mongodb_db]

    return(db)


def queryClassA(chain: str, endpoint: str) -> None:
    ''' Performs covalent class A requests
    '''

    url = f'https://api.covalenthq.com/v1/{chain}/address/{env.matic_wallet}/{endpoint}/?key={env.key}'

    response = requests.get(url)
    response = response.text
    response = json.loads(response)

    timestamp = response['data']['updated_at']
    timestamp = dateutil.parser.parse(timestamp)
    timestamp = timestamp.replace(tzinfo=pytz.timezone(env.tz))

    response['timestamp'] = timestamp

    return(response)


def getMaticBalances(DB: pymongo.MongoClient):
    '''
    '''

    response = queryClassA('137', 'balances_v2')
    for item in response['data']['items']:
        decimals = item['contract_decimals']
        balance = int(item['balance'])
        balance = balance / (10 ** decimals)

        DB['matic_balances'].insert_one(
            {
                'contract_ decimals' : item['contract_decimals'],
                'contract_name' : item['contract_name'],
                'contract_ticker_symbol' : item['contract_ticker_symbol'],
                'contract_address' : item['contract_address'],
                'supports_erc' : item['supports_erc'],
                'logo_url' : item['logo_url'],
                'type' : item['type'],
                'balance' : balance,
                'quote_rate' : item['quote_rate'],
                'quote' : item['quote'],
                'nft_data' : item['nft_data'],
                'timestamp' : response['timestamp']
            }
        )
        print(f"{item['contract_ticker_symbol']}: {balance}")



def run():
    '''
    '''
    
    while True:
        DB = connectDB()
        while True:
            try:
                getMaticBalances(DB)
            except Exception as e:
                print(e)
            
            print(f"Sleeping {env.interval} seconds.")
            time.sleep(env.interval)



if __name__ == '__main__':

    run()