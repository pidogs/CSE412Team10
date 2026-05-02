# Getting started

## Create a virtual environment
`python -m venv venv`

## Activate Windows
`venv\Scripts\activate`
## Activate Mac or Linux
`source venv/bin/activate`

## Install libraries
`pip install -r requirements.txt`

## Start the server
`python app.py`

# dump the database
`pg_dump -U aircraft_db -h 127.0.0.1 -p 5432 aircraft_db > aircraft_db_dump.sql`

