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

## Running the server

Just run the run.py file, that will run the flask server:\
`python run.py`
