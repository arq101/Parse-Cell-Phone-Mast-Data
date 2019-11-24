# Technical Exercise To Parse and Process CSV Data

A script to process and report on data pertaining to cell phone tower masts.

## Set up your virtualenv with Python 3.7

Assuming virtualenv is already installed on your system.  
If using a virtualenvwrapper then set up a virtual environment for this project 
eg.
```
mkvirtualenv -p /usr/bin/python3.7 -a [path to project] [virtualenv name]
```
Otherwise set up your virtual environment as you normally would.  

Once your virtualenv is active, from the project root dir install the necessary dependencies

```
pip3 install -r requirements.txt
```

## Run unittests
From the project root ...
``` 
pytest -v test_run_phone_mast_analysis_report.py
```


## Script Usage
```
python run_phone_mast_analysis_report.py -h
```

## Requirement 1 - Top Rent Info
Display information on top 5 sites with current rent in ascending order
```
python run_phone_mast_analysis_report.py ./sample_data/input_dataset.csv -top_rents 5
``` 


## Requirement 2 - All Mast Data Matching Lease Years
Display information full data set for masts that have number of lease years equal to 25
```
python run_phone_mast_analysis_report.py ./sample_data/input_dataset.csv -lease_years 25
``` 

## Requirement 3 - Tenants and Number of Mast Sites
Display information on tenant names and numbner of sites associated to each tenant
```
python run_phone_mast_analysis_report.py ./sample_data/input_dataset.csv -tenants 
```


## Requirement 4 - Leases Starting Between Given Start Dates
Display information on rental mast sites where lease start date is between 2 given dates
```
python run_phone_mast_analysis_report.py ./sample_data/input_dataset.csv -lease_starting_range 1999-06-01 2007-08-31
``` 
