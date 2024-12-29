import requests
import json
import pandas as pd
import os
from airflow.models import Variable
from datetime import datetime, timedelta

#now  = datetime.now()
#dt_now_string = now.strftime("%Y-%m-%d-%H-%M-%S")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), 'data')
os.makedirs(OUTPUT_DIR, exist_ok=True)

def extract_realtor_data(**kwargs):
    api_credentials = Variable.get("redfin_api_credentials", deserialize_json=True)
    url = kwargs['url']
    headers = {
        "x-rapidapi-key": api_credentials["x-rapidapi-key"],
        "x-rapidapi-host": api_credentials["x-rapidapi-host"]
    }
    
    querystring = kwargs['querystring']
    dt_string = kwargs['date_string']
    
    try:
        response = requests.get(url, headers=headers, params=querystring)
        response.raise_for_status()
        data = response.json()
        
        # Save to local data directory
        output_file = os.path.join(OUTPUT_DIR, f'Redfin_data_{dt_string}.json')
        with open(output_file, 'w') as f:
            json.dump(data, f)
            print(f"Data saved locally to: {output_file}")
            
        return output_file
        
    except requests.exceptions.RequestException as e:
        print(f"Error making API request: {e}")
        raise
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON response: {e}")
        raise
