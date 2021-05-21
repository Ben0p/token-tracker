import requests



def getBnbBalance(address: str, api_key: str) -> float:
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

    return(bnb_balance)