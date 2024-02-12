# WildFires-DataSet-Generator

A dynamic WildFires Dataset Generator for Artificial Intelligence serving WildFires Detection.

## Installation
This project requires conda to be installed. You can find conda's documentation for installation [here](https://conda.io/projects/conda/en/latest/user-guide/install/index.html)

Create a virtual environment (venv):\
`conda create -p .venv python`

Initialize conda (if not done already):\
`conda init`

Activate the environment:\
`conda activate ./.venv`

Execute the following command to install all required packages (except pyhdf):\
`pip install -r requirements.txt`

Then execute the following command to install pyhdf:\
`conda install -c conda-forge pyhdf`

That's it for the installation.

## Populate the database

The project was initially developped for MySQL, so we recommand using it for this project. To configure the database for this project, add a `.env` file in the main folder, copy attributes from `.env.example` into `.env`. For the DATABASE_URL, it should be like this:\
`DATABASE_URL=mysql+mysqlconnector://<user>:<password>@<host>:<port>/<database_name>`

Every `<attribute>` should be replaced according to your database and where it's hosted.

After successfully configuring the database, you can populate it by executing the `populate_database.py` script. Ex:\
`python populate_database.py --lat_min=36 --lat_max=36.5 --lng_min=1 --lng_max=1.5 --start_date=1/7/2015 --end_date=10/7/2015`

You can see more details about this sccript by executing:\
`python populate_database.py -h`

## Running the server

First make sure that the database is online and just run the `run.py` file, that will run the flask server:\
`python run.py`

Access the user web portal:\
`http://localhost:5000`
