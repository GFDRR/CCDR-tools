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

# Load env vars from dotenv file
from dotenv import dotenv_values

config     = dotenv_values(".env")
DATA_DIR   = config["DATA_DIR"]
OUTPUT_DIR = config["OUTPUT_DIR"]
CACHE_DIR  = config["CACHE_DIR"]

# Ensure output and cache dirs exist
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(CACHE_DIR,  exist_ok=True)
