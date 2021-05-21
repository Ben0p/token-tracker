import requests
import hmac
import hashlib
import time
import urllib.parse
import json
import http.client as httplib




'''
    Performs some coinspot API requests and returns the responses
'''



def query(key: str, secret: str, path: str) -> list:
    ''' Creates, signes and posts the API request
        Returns dictionary response
    '''

    # Convert secret to bytes
    secret = secret.encode('utf-8')

    # Construct the nonce
    nonce = int(time.time()*1000000)
    postdata = {
        'nonce' :  nonce
    }

    # Convert parameters to json
    params = json.dumps(postdata, separators=(',', ':'))

    # Sign the message with the secret using sha512
    signedMessage = hmac.new(secret, params.encode('utf-8'), hashlib.sha512).hexdigest()

    # Construct the headers
    headers = {}
    headers['Content-type'] = 'application/json'
    headers['Accept'] = 'text/plain'
    headers['key'] = key
    headers['sign'] = signedMessage

    # Coinspot url
    endpoint = "www.coinspot.com.au"

    # Create connection
    conn = httplib.HTTPSConnection(endpoint)

    # Perform the POST
    conn.request("POST", path, params, headers)
    response = conn.getresponse()

    #print response.status, response.reason
    response_data = response.read()

    # Decode and convert json to dict then get the balances list
    response_data = response_data.decode("utf-8")
    response_data = json.loads(response_data)
    response_data = response_data['balances']

    # Close connection
    conn.close()

    return(response_data)



def getBalances(key: str, secret: str) -> dict:
    
    path = '/api/v2/ro/my/balances'

    response = query(key, secret, path)
    
    return(response)



if __name__ == "__main__":

    key = "your_key"
    secret = "your_secret"

    balances = getBalances(key, secret)

    total_aud = 0

    for balance in balances:
        for coin in balance:
            
            aud = float(balance[coin]['audbalance'])
            total_aud += aud

            print(f"{coin}:")
            print(f"    Balance: {balance[coin]['balance']}")
            print(f"       Rate: {balance[coin]['rate']}")
            print(f"       $AUD: {aud}")

    print(f" Total $AUD: {total_aud}")