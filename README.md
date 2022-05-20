# Install manual

1. Download the gtfs data from https://transitfeeds.com/p/praha/801 and save the `gtfs.zip` into the project folder
2. Create a virtual environment `virtualenv /path/to/new/virtual/environment -p python3`
3. Activate the virtual environment `source /path/to/venv/bin/activate`
4. Install the necessary requirements `pip3 install -r requirements.txt`
5. Create a MongoDB database if you do not have one already https://www.mongodb.com/basics/create-database 
6. Go to `db_utils.py` and fill your MongoDB URI and database name
7. Run `db_seed.py` and check your database if 4 collections with documents have been created
8. Run `app.py` to start the server