# Solarman 2 TimescaleDB

## Rationale

I wanted to keep historical data from Solarman app, so I created this Python code to scrape selected data from the API and store it in TimescaleDB.

## Requirements

* Python 3.12+ (but 3.8+ should work, too)
* requests
* psycopg2

## Deployment

Set the environmental variables (see `.env.example`) and execute `solarman2timescaledb.py` script. You can also build a Docker image.

## To Do:

* add info where to get API keys
* sample docker-compose file
* CI pipeline for building Docker image
* a way of creating DB schema automatically
* describe how to obtain an example JSON
* add Grafana dashboard JSON
