# Required libraries
import tempfile, os, gc
import warnings
from collections import OrderedDict

import numpy as np
import pandas as pd
import geopandas as gpd
from tqdm import tqdm

import rasterio
import xarray as xr
import rioxarray as rxr
from rasterstats import gen_zonal_stats, zonal_stats

import requests
from shapely.geometry import shape

# Load env vars from dotenv file
from dotenv import dotenv_values

config     = dotenv_values(".env")
DATA_DIR   = config["DATA_DIR"]
OUTPUT_DIR = config["OUTPUT_DIR"]
CACHE_DIR  = config["CACHE_DIR"]

# Ensure output and cache dirs exist
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(CACHE_DIR,  exist_ok=True)

# Define the REST API URL
rest_api_url = "https://services.arcgis.com/iQ1dY19aHwbSDYIF/ArcGIS/rest/services/World_Bank_Global_Administrative_Divisions_VIEW/FeatureServer"

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
    'LCR': 'LAC',           # Latin America and Caribbean
    'ECA': 'ASIA',          # East Europe and Central Asia
    'Other': 'GLOBAL',      # North America, Europe, Japan, Korea, Australia and New Zealand
}