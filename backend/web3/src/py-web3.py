from env import env
import abis
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


def get_balances(
        web3: Web3,
        tokens: list
    ) -> dict:
    '''Get ETH Balance'''

    wei_balance = web3.eth.getBalance(env.eth_wallet)
    eth_balance = web3.fromWei(wei_balance, 'ether')

    for token in tokens:
        token_contract = web3.eth.contract(address=token['address'], abi=abis.abis[token['symbol']])
        token_balance = token_contract.functions.balanceOf(env.eth_wallet).call()
        print(token_balance)

    balances = {
        'wei' : wei_balance,
        'eth' : eth_balance
    }    

    return(balances)


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

    # Balances
    balances = get_balances(web3, eth_tokens)
    print(f"ETH: {balances['eth']}")

    # Block info
    block = latest_block(web3)


if __name__ == "__main__":
    run()