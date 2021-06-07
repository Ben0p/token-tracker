from env import env

import requests
import time
import json
import pymongo
import urllib
from datetime import datetime
import pytz



def connectDB() -> pymongo.MongoClient:
    ''' Connects to a pymongo DB (specified in the env)
        Returns the MongoClient connection object
    '''

    username = urllib.parse.quote_plus(env.mongodb_user)
    password = urllib.parse.quote_plus(env.mongodb_pass)

    client = pymongo.MongoClient(f'mongodb://{username}:{password}@{env.mongodb_host}:{env.mongodb_port}')

    db = client[env.mongodb_db]

    return(db)


def getBSCTokens(address: str, DB: pymongo.MongoClient) -> None:
    ''' Input BSC wallet address <str>
        Returns a list of BNC tokens held in wallet <list>
        Uses free bitquery API (10 per minute)
    '''

    print('##############')
    print('# BSC Tokens #')
    print('##############')

    # GraphQL Query
    query = f'''{{ethereum(network: bsc) {{
                    address(address: {{is: "{address}"}}) {{
                        balances {{
                            currency {{
                                symbol
                                address
                                decimals
                                name
                            }}
                            value
                        }}
                    }}
                }}
            }}'''

    url = 'https://graphql.bitquery.io'

    while True:
        try:
            tokens = requests.post(url, json={'query': query})
            tokens = tokens.json()
            break
        except json.decoder.JSONDecodeError:
            print("Unable to query bitquery, wait 10s...")
            time.sleep(10)
    
    tokens = tokens['data']['ethereum']['address'][0]['balances']
    # Append timestamp
    timestamp = datetime.now()
    timestamp = timestamp.replace(tzinfo=pytz.timezone(env.tz))

    for token in tokens:

        DB['bsc_balances'].insert_one(
            {
                'symbol' : token['currency']['symbol'],
                'address' : token['currency']['address'],
                'decimals' : token['currency']['decimals'],
                'name' : token['currency']['name'],
                'value' : token['value'],
                'timestamp' : timestamp
            }
        )
        print(f"{token['currency']['symbol']} : {token['value']}")


def getETHTokens(address: str, DB: pymongo.MongoClient) -> list:
    ''' Input ETH wallet address <str>
        Returns a list of ETH tokens held in wallet <list>
        Uses free bitquery API (10 per minute)
    '''

    print('##############')
    print('# ETH Tokens #')
    print('##############')

    # GraphQL Query
    query = f'''{{ethereum(network: ethereum) {{
                    address(address: {{is: "{address}"}}) {{
                        balances {{
                            currency {{
                                symbol
                                address
                                decimals
                                name
                            }}
                            value
                        }}
                    }}
                }}
            }}'''

    url = 'https://graphql.bitquery.io'
    while True:
        try:
            tokens = requests.post(url, json={'query': query})
            tokens = tokens.json()
            break
        except json.decoder.JSONDecodeError:
            print("Unable to query bitquery, wait 10s...")
            time.sleep(10)
    
    tokens = tokens['data']['ethereum']['address'][0]['balances']
    # Append timestamp
    timestamp = datetime.now()
    timestamp = timestamp.replace(tzinfo=pytz.timezone(env.tz))

    for token in tokens:

        DB['eth_balances'].insert_one(
            {
                'symbol' : token['currency']['symbol'],
                'address' : token['currency']['address'],
                'decimals' : token['currency']['decimals'],
                'name' : token['currency']['name'],
                'value' : token['value'],
                'timestamp' : timestamp
            }
        )
        print(f"{token['currency']['symbol']} : {token['value']}")


def getWBNBHoldings(address: str):
    ''' Input BSC wallet or token address <str>
        Returns a the amount of Wrapped BNB held (WBNB)
        This also indicates the Token/WBNB liquidity (LP)
    '''

    # GraphQL Query
    query = f'''{{ethereum(network: bsc) {{
                    address(address: {{is: "{address}"}}) {{
                        balances(currency: {{is: "0xbb4cdb9cbd36b01bd1cbaebf2de08d9173bc095c"}}) {{
                            currency {{
                                symbol
                                address
                                decimals
                                name
                            }}
                            value
                        }}
                    }}
                }}
            }}'''

    url = 'https://graphql.bitquery.io'

    while True:
        try:
            tokens = requests.post(url, json={'query': query})
            tokens = tokens.json()
            break
        except json.decoder.JSONDecodeError:
            print("Unable to query bitquery, wait 10s...")
            time.sleep(10)
    
    return(tokens['data']['ethereum']['address'][0]['balances'][0]['value'])


def run():
    '''
    '''

    while True:

        DB = connectDB()

        while True:
            getBSCTokens(env.bsc_wallet, DB)
            getETHTokens(env.bsc_wallet, DB)

            print(f"Sleeping {env.interval} seconds.")
            time.sleep(env.interval)



if __name__ == "__main__":

    run()