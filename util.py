import json 
# Constants
JSON_FILE = 'user_data.json'
DEFAULT_SETTINGS = {    
    'exchange': 'binance',
    'alarm': '15m',
    'symbol': 'BTC/USDT',
    'timeframe': '15m',
    'ohlc': 'OHLC',
}

# --- JSON file utility functions ---
def read_json_data():
    """Reads user data from the JSON file."""
    try:
        with open(JSON_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def write_json_data(data):
    """Writes user data back to the JSON file."""
    with open(JSON_FILE, 'w') as f:
        json.dump(data, f, indent=4)

def get_user_settings(user_id):
    """Retrieves or creates user settings from the JSON data."""
    data = read_json_data()
    user_id_str = str(user_id)
    if user_id_str not in data:
        data[user_id_str] = DEFAULT_SETTINGS
        write_json_data(data)
    return data[user_id_str]

def update_user_settings(user_id, new_settings):
    """Updates a user's settings and saves to the JSON file."""
    data = read_json_data()
    user_id_str = str(user_id)
    data[user_id_str] = new_settings
    write_json_data(data)
    print(data)

