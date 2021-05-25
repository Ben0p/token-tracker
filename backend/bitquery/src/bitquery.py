from env import env

import requests
import time
import json



def getBSCTokens(address: str) -> list:
    ''' Input BSC wallet address <str>
        Returns a list of BNC tokens held in wallet <list>
        Uses free bitquery API (10 per minute)
    '''

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

    return(tokens)


def getETHTokens(address: str) -> list:
    ''' Input ETH wallet address <str>
        Returns a list of ETH tokens held in wallet <list>
        Uses free bitquery API (10 per minute)
    '''

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

    return(tokens)


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




if __name__ == "__main__":

    '''
    # Test
    bsc_tokens = getBSCTokens(env.bsc_wallet)
    eth_tokens = getETHTokens(env.bsc_wallet)

    tokens = bsc_tokens + eth_tokens

    for token in tokens:
        print(token)
    '''

    mars_holdings = getWBNBHoldings('0xbD46105d4303d76617F3E1788648CB9486084533')

    print(mars_holdings)
   