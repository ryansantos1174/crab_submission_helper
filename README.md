# Overview
This project allows one to easily submit, monitor the status of, and resubmit crab jobs. There are three command available: status, resubmit, and submit. Important information for each command will be documented below. 
# Setup 
## Script Setup
The automatic logging of job completion is controlled through google sheets. As such, you need to interface with Google's API. In order to store the API credentials and the google sheet identification, we need to create a .env file. 
'''
touch .env
'''
Within this file fill in the following information: 
'''
GOOGLE_SHEET_ID=<GOOGLE SHEET ID>
CREDENTIALS=<SERVICE ACCOUNT CREDENTIALS JSON>
'''

You only need to set this up once per google sheet per service account (ie. you probably don't have to procure these items yourself ask someone to securely share them with you). 
## Installation
The project can be installed as a local package. From scratch the instructions are: 
- git clone https://github.com/ryansantos1174/crab_submission_helper.git
- cd crab_submission_helper
- python3 -m build
- pip install -e . 

This will give you access the command line function crab_helper which can be used to submit your jobs
## Crontab Setup
TODO 

# Code Overview
The project is broken up into the following directories: configs, templates, lib, src, tests.

## configs
The configs directory is where you will store information that will help you submit jobs. This directory includes datasets.toml which includes all of the datasets necessary to process our selections for each year and era. The selections.toml file is a mapping of selections to which dataset they should be using. 

## templates
The submit command makes use of a templating system to generate the necessary changes to the submission files. This is a very simple templating system. It replaces strings of the form "__VALUE__" with a corresponding value in a dictionary {"VALUE": "replacement"}. You can make your own templates with this in mind. 

## lib
This is a self explanatory directory that just contains the python files that define functions that are used throughout the project. 

## src
This is where the main script and the bash script used for crontab are kept. 

## tests
This is where tests can be implemented to ensure that the code works as intended. The testing framework is pytest. You can run all of the tests within the test directory by running: 

'''
pytest 
'''
in the project root directory. 
