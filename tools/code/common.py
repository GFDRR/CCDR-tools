# This file includes common configuration elements used by the script.

import os
from dotenv import dotenv_values, find_dotenv

config = dotenv_values(find_dotenv())
DATA_DIR   = config["DATA_DIR"]
OUTPUT_DIR = config["OUTPUT_DIR"]
CACHE_DIR  = config["CACHE_DIR"]

# Ensure output and cache dirs exist
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(CACHE_DIR,  exist_ok=True)

# Define the REST API URL
rest_api_url = "https://services.arcgis.com/iQ1dY19aHwbSDYIF/ArcGIS/rest/services/World_Bank_Global_Administrative_Divisions_VIEW/FeatureServer"
worldpop_url = "https://data.worldpop.org/GIS/Population/"
stac_search_url = "https://geoservice.dlr.de/eoc/ogc/stac/v1/search"


# Mapping of administrative levels to field names for WB GAD dataset
adm_field_mapping = {
    0: {'code': 'HASC_0', 'name': 'NAM_0'},
    1: {'code': 'HASC_1', 'name': 'NAM_1'},
    2: {'code': 'HASC_2', 'name': 'NAM_2'},
    # Add mappings for additional levels as needed
}

wb_to_region = {
    'AFR': 'AFRICA',        # Sub-Saharan Africa
    'MENA': 'AFRICA',       # Middle East and North Africa
    'EAP': 'ASIA',          # East Asia and Pacific
    'SAR': 'ASIA',          # South Asia
    'ECA': 'ASIA',          # East Europe and Central Asia
    'LCR': 'LAC',           # Latin America and Caribbean
    'Other': 'GLOBAL',      # North America, Europe, Japan, Korea, Australia and New Zealand
}