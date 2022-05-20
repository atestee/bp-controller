# Install manual

1. Create a virtual environment `virtualenv /path/to/new/virtual/environment -p python3`
2. Activate the virtual environment `source /path/to/venv/bin/activate`
3. Install the necessary requirements `pip3 install -r requirements.txt`
4. Create a MongoDB database if you do not have one already https://www.mongodb.com/basics/create-database 
5. Go to `db_utils.py` and fill your MongoDB URI and database name
6. Run `db_seed.py` and check your database if 4 collections with documents have been created
7. Run `app.py` to start the server