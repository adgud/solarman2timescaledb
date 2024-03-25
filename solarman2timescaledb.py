#!/usr/bin/env python3

import config
from datetime import datetime, timezone, timedelta
import os
import hashlib
import json
import psycopg2
import requests
import random
import time

API_BASE_URL = "https://globalapi.solarmanpv.com"

SCRAPE_INTERVAL = os.environ.get('SCRAPE_INTERVAL', 310)
EMAIL = os.environ.get('EMAIL')
PASSWORD = os.environ.get('PASSWORD')
APP_ID = os.environ.get('APP_ID')
APP_SECRET = os.environ.get('APP_SECRET')
INVERTER_SN = os.environ.get('INVERTER_SN')
POSTGRES_HOST = os.environ.get('POSTGRES_HOST')
POSTGRES_DB = os.environ.get('POSTGRES_DB')
POSTGRES_USER = os.environ.get('POSTGRES_USER')
POSTGRES_PASSWORD = os.environ.get('POSTGRES_PASSWORD')


def name_unit2column(name, unit=None):
    column_name = name.lower().replace(" ", "_").replace("-", "_").replace(" ", "_").replace("/", "_").replace("(", "_").replace(")", "_")
    if unit:
        unit = 'percent' if unit == '%' else unit
        unit = 'celsius' if unit == '℃' else unit
        column_name += f"_{unit.lower()}"
    return column_name


def get_oauth_token():
    token_url = f"{API_BASE_URL}/account/v1.0/token?appId={APP_ID}&language=en"
    password_hash = hashlib.sha256(PASSWORD.encode('utf-8')).hexdigest()
    
    body = {
        "appSecret": APP_SECRET,
        "email": EMAIL,
        "password": password_hash
    }
    
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': ''
    }
    
    response = requests.post(token_url, data=json.dumps(body), headers=headers)
    if response.status_code == 200 and response.json()['access_token']:
        return response.json()['access_token']
    else:
        raise Exception(f"Failed to get OAuth token: {response.status_code} {response.text}")


def get_current_data(oauth_token):
    current_data_url = f"{API_BASE_URL}/device/v1.0/currentData?appId={APP_ID}&language=en"
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {oauth_token}',
        'User-Agent': ''
    }
    
    body = {
        'deviceSn': INVERTER_SN
    }
    
    response = requests.post(current_data_url, data=json.dumps(body), headers=headers)
    if response.status_code == 200:
        return response.json()  # Return the response JSON (which includes the current data)
    else:
        raise Exception(f"Failed to post current data: {response.status_code} {response.text}")


def generate_postgresql_insert_query(table_name, items, timestamp):
    columns = ['time'] + [name_unit2column(item['name'], item['unit']) for item in items]
    values = [timestamp] + [item['value'] for item in items]
    
    columns_str = ', '.join(columns)
    values_placeholders = ', '.join(['%s'] * len(values))

    query = f"INSERT INTO {table_name} ({columns_str}) VALUES ({values_placeholders});"
    
    return query, values

def main():
    print(f"Starting loop with interval {SCRAPE_INTERVAL} seconds")
    while True:
        oauth_token = get_oauth_token()
        current_data = get_current_data(oauth_token)
        data_list = current_data["dataList"]
        print(f"Collection time: {current_data['collectionTime']}")
        print(f"Data list length: {len(data_list)}")

        battery_items = [
            item for item in data_list if item.get("name") in config.BATTERY_ITEM_NAMES
        ]
        consumption_items = [
            item for item in data_list if item.get("name") in config.CONSUMPTION_ITEM_NAMES
        ]
        grid_items = [
            item for item in data_list if item.get("name") in config.GRID_ITEM_NAMES
        ]
        production_items = [
            item for item in data_list if item.get("name") in config.PRODUCTION_ITEM_NAMES
        ]
        temperature_items = [
            item for item in data_list if item.get("name") in config.TEMPERATURE_ITEM_NAMES
        ]

        conn = psycopg2.connect(
            host=POSTGRES_HOST,
            port="5432",
            dbname=POSTGRES_DB,
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD,
        )
        cur = conn.cursor()
        timestamp = datetime.utcnow()

        query, values = generate_postgresql_insert_query('battery', battery_items, timestamp)
        cur.execute(query, values)
        query, values = generate_postgresql_insert_query('consumption', consumption_items, timestamp)
        cur.execute(query, values)
        query, values = generate_postgresql_insert_query('grid', grid_items, timestamp)
        cur.execute(query, values)
        query, values = generate_postgresql_insert_query('production', production_items, timestamp)
        cur.execute(query, values)
        query, values = generate_postgresql_insert_query('temperature', temperature_items, timestamp)
        cur.execute(query, values)

        conn.commit()
        cur.close()
        conn.close()
        print(f"Data written to database with timestamp {str(timestamp)}") 
        time.sleep(int(SCRAPE_INTERVAL))

if __name__ == "__main__":
    main()