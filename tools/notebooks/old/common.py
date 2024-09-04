# Required libraries
import tempfile, os
import warnings
from collections import OrderedDict

import requests
import json


import numpy as np
import pandas as pd
import geopandas as gpd
from tqdm import tqdm

import rasterio
import xarray as xr
import rioxarray as rxr
from rasterstats import gen_zonal_stats, zonal_stats

import contextily as ctx
# from contextily import Place

# Addresses SSL error when interacting with worldpop data
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

import matplotlib.pyplot as plt


# import widgets
import ipywidgets as widgets
from ipywidgets import interact, interact_manual, Layout, Box, HBox, VBox
import IPython.display
from IPython.display import display, clear_output


# Load env vars from dotenv file
from dotenv import dotenv_values

config = dotenv_values(".env")
DATA_DIR = config["DATA_DIR"]
OUTPUT_DIR = config["OUTPUT_DIR"]
CACHE_DIR = config["CACHE_DIR"]

# Ensure output and cache dirs exist
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(CACHE_DIR, exist_ok=True)