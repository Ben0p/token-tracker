from env import env
from web3 import Web3
import urllib
import pymongo
import json


def connect_rpc(url: str) -> Web3:
    '''Connects to the rpc ethereum node'''

    web3 = Web3(Web3.HTTPProvider(url))

    return(web3)


def connect_mongo() -> pymongo.MongoClient:
    '''Connects to MongoDB and returns MongoClient'''

    username = urllib.parse.quote_plus(env.mongodb_user)
    password = urllib.parse.quote_plus(env.mongodb_pass)

    client = pymongo.MongoClient(f'mongodb://{username}:{password}@{env.mongodb_host}:{env.mongodb_port}')

    db = client[env.mongodb_db]

    return(db)


def get_eth_tokens(
        db: pymongo.MongoClient
    ) -> list:
    '''Get ETH tokens list from database'''
    
    eth_tokens = db['eth_tokens'].find()

    return(eth_tokens)


def get_contract(
        web3: Web3,
        token: dict
    ):
    '''Gets total supply of a token'''

    checksum_address = Web3.toChecksumAddress(token['address'])
    contract = web3.eth.contract(address=checksum_address, abi=token['abi'])

    return(contract)


def get_info(
        contract,
        token: dict
    ) -> dict:
    '''Gets info of a token contract'''

    if 'name' not in token:
        # Get token name
        token['name'] = contract.functions.name().call()
        print(token['name'])

    if 'symbol' not in token:
        # Get token symbol
        token['symbol'] = contract.functions.symbol().call()
    
    if 'decimals' not in token:
        # Get decimals
        token['decimals'] = contract.functions.decimals().call()

    if 'supply' not in token:
        # Get total supply
        supply = contract.functions.totalSupply().call()
        if token['decimals'] > 0:
            supply = supply / (10**token['decimals'])
        
        token['supply'] = supply
    
    return(token)


def get_balance(
    contract,
    wallet: str
    ) -> float:
    '''Get token balance of a wallet'''

    # Find function by signature to handle overloading
    balance_function = contract.get_function_by_signature('balanceOf(address)')
    # Call function
    balance = balance_function(wallet).call()

    return(balance)


def latest_block(web3: Web3) -> dict:
    '''Returns the latest block information'''

    return(web3.eth.get_block('latest'))


def run():
    '''Main run loop'''

    # Connect RPC
    web3 = connect_rpc(env.infura_url)
    print(f"Connected: {web3.isConnected()}")
    print(f"Block number: {web3.eth.blockNumber}")

    # Connect Mongo
    db = connect_mongo()

    # Get eth tokens from Mongo
    eth_tokens = get_eth_tokens(db)

    for token in eth_tokens:
        if token['address'] != '-':
            contract = get_contract(web3, token)
            token = get_info(contract, token)

            balance = get_balance(contract, env.eth_wallet)
            print(f"{token['name']} balance: {balance}")





if __name__ == "__main__":
    run()