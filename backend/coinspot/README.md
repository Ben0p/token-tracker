# CoinSpot bot

Uses the [CoinSpot API](https://www.coinspot.com.au/v2/api) to retrieve coin listings, prices, coins held etc. Stores the information in MongoDB with time stamps. This script is useful in conjunction with other scripts for trading.

**USE AT YOUR OWN RISK**

### Environment file
Put your API key and secret in the .\src\env.py file as a class.
Example:
```
class env():
    coinspot_key = "YOURREADONLYCOINSPOTKEY"
    coinspot_secret = "YOURCOINSPOTREADONLYSECRET"
    mongodb_host = "mongo ip or hostname"
    mongodb_db = "mongo database"
```

*env.py files are ignored in the .gitignore file for obvious reasons*


### Requirements
- Designed to run in docker otherwise run the coinspot.py script directly.
- MongoDB (can also be a docker container)
- Python requirements in the requirements.py file.
