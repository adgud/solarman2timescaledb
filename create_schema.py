#!/usr/bin/env python

import psycopg2
import config
from solarman2timescaledb import name_unit2column

def determine_postgresql_type(python_variable):
    if '.' in python_variable:
        return "double precision"
    elif python_variable.isdigit():
        return "integer"
    if isinstance(python_variable, str):
        return "text"
    else:
        raise ValueError("Unsupported Python variable type.")

import json
def load_json_file(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

json_data = load_json_file('example.json')
data_list = json_data["dataList"]
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

create_battery_table_query = "CREATE TABLE battery (time timestamptz not null, "
for item in battery_items:
    column_name = name_unit2column(item['name'], item['unit'])
    column_type = determine_postgresql_type(item['value'])
    create_battery_table_query += f"{column_name} {column_type},"
create_battery_table_query = create_battery_table_query.rstrip(',') + ");"
print(create_battery_table_query)
print("SELECT create_hypertable('battery', by_range('time'));")

create_consumption_table_query = "CREATE TABLE consumption (time timestamptz not null, "
for item in consumption_items:
    column_name = name_unit2column(item['name'], item['unit'])
    column_type = determine_postgresql_type(item['value'])
    create_consumption_table_query += f"{column_name} {column_type},"

create_consumption_table_query = create_consumption_table_query.rstrip(',') + ");"
print(create_consumption_table_query)
print("SELECT create_hypertable('consumption', by_range('time'));")

create_grid_table_query = "CREATE TABLE grid (time timestamptz not null, "
for item in grid_items:
    column_name = name_unit2column(item['name'], item['unit'])
    column_type = determine_postgresql_type(item['value'])
    create_grid_table_query += f"{column_name} {column_type},"
create_grid_table_query = create_grid_table_query.rstrip(',') + ");"
print(create_grid_table_query)
print("SELECT create_hypertable('grid', by_range('time'));")

create_production_table_query = "CREATE TABLE production (time timestamptz not null, "
for item in production_items:
    column_name = name_unit2column(item['name'], item['unit'])
    column_type = determine_postgresql_type(item['value'])
    create_production_table_query += f"{column_name} {column_type},"
create_production_table_query = create_production_table_query.rstrip(',') + ");"
print(create_production_table_query)
print("SELECT create_hypertable('production', by_range('time'));")


create_temperature_table_query = "CREATE TABLE temperature (time timestamptz not null, "
for item in temperature_items:
    column_name = name_unit2column(item['name'], item['unit'])
    column_type = determine_postgresql_type(item['value'])
    create_temperature_table_query += f"{column_name} {column_type},"
create_temperature_table_query = create_temperature_table_query.rstrip(',') + ");"
print(create_temperature_table_query)
print("SELECT create_hypertable('temperature', by_range('time'));")