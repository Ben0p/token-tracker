import requests



def getBSCTokenInfo(address: str) -> dict:
    ''' Input the token address <str>
        Returns the token information <dict>
        Uses pancakeswap API (unknown limit)
    '''

    token_info_url = f"https://api.pancakeswap.info/api/v2/tokens/{address}"

    token_info = requests.get(token_info_url)
    token_info = token_info.json()
    
    return(token_info)