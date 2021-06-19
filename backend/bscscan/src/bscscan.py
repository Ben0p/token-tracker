from env import env

import requests
import pymongo
import urllib
import time


def connectDB() -> pymongo.MongoClient:
    ''' Connects to a pymongo DB (specified in the env)
        Returns the MongoClient connection object
    '''

    username = urllib.parse.quote_plus(env.mongodb_user)
    password = urllib.parse.quote_plus(env.mongodb_pass)

    client = pymongo.MongoClient(f'mongodb://{username}:{password}@{env.mongodb_host}:{env.mongodb_port}')

    db = client[env.mongodb_db]

    return(db)


def writeLog(DB: pymongo.MongoClient, log: dict) -> None:
    '''
    '''

    DB['log'].insert_one(log)


def getBnbBalance(address: str, api_key: str, DB: pymongo.MongoClient) -> None:
    ''' address: Wallet address <str>
        api_key: BSCScan API key <str>
        Returns BNB balance of wallet <float>
    '''

    # Construct API URL from params
    bnb_balance_url = f"https://api.bscscan.com/api?module=account&action=balance&address={address}&tag=latest&apikey={api_key}"

    # Perform request, extract balance and convert value (BNB is 18 decimals)
    bnb_balance = requests.get(bnb_balance_url)
    bnb_balance = bnb_balance.json()
    bnb_balance = int(bnb_balance['result']) / (10**18)





def run():
    ''' 
    ''' 

    while True:

        DB = connectDB()

        while True:
            getBnbBalance(env.bsc_wallet, env.bscscan_key, DB)
        
            time.sleep(env.interval)



if __name__ == "__main__":

    run()