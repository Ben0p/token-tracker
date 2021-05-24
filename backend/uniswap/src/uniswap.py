import requests
import json
import time



def getETHValue():

    # GraphQL Query
    query = f'''{{
        token(id: "0x6b175474e89094c44da98b954eedeac495271d0f"){{
            name
            symbol
            decimals
            derivedETH
            tradeVolumeUSD
            totalLiquidity
        }}
    }}'''

    url = 'https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v2'

    dai = requests.post(url, json={'query': query})
    dai= dai.json()
    dai_value = float(dai['data']['token']['derivedETH'])
    
    eth_value = 1/dai_value

    return(eth_value)   


def getTokenValue(address: str) -> list:


    # GraphQL Query
    query = f'''{{
        token(id: "{address}"){{
            name
            symbol
            decimals
            derivedETH
            tradeVolumeUSD
            totalLiquidity
        }}
    }}'''

    url = 'https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v2'

    try:
        token = requests.post(url, json={'query': query})
        token = token.json()
        token_eth = float(token['data']['token']['derivedETH'])
    except TypeError:
        token_eth = 0
    
    eth_usd = getETHValue()

    token_usd = token_eth * eth_usd

    return(token_usd)


if __name__ == "__main__":

    token = "0xdacd69347de42babfaecd09dc88958378780fb62"

    eth_value = getETHValue()
    print(f"ETH/USD: {eth_value}")

    token_value = getTokenValue(token)
    print(f"Token/USD: {token_value}")
