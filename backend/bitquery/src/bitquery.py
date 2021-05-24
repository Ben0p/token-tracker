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