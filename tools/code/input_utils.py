import os
from osgeo import gdal
import numpy as np
import common
import requests
import geopandas as gpd
import shutil
from shapely.geometry import shape, MultiPolygon
from shapely.geometry.base import BaseGeometry
from tqdm import tqdm

DATA_DIR = common.DATA_DIR
OUTPUT_DIR = common.OUTPUT_DIR

# Function to get the correct layer ID based on administrative level
def get_layer_id_for_adm(adm_level):
    layers_url = f"{common.rest_api_url}/layers"
    target_layer_name = f"WB_GAD_ADM{adm_level}"

    response = requests.get(layers_url, params={'f': 'json'})
    
    if response.status_code != 200:
        print(f"Failed to fetch layers. Status code: {response.status_code}")
        return None

    layers_info = response.json().get('layers', [])
    
    layers = [elem['id'] for elem in layers_info if elem['name'] == target_layer_name]
    if len(layers) == 0:
        raise ValueError(f"Layer matching {target_layer_name} not found.")
    return layers[0]
    

# Function to fetch the ADM data using the correct layer ID
def get_adm_data(country: str, adm_level):
    layer_id = get_layer_id_for_adm(adm_level)
    
    query_url = f"{common.rest_api_url}/{layer_id}/query"
    params = {
        'where': f"ISO_A3 = '{country}'",
        'outFields': '*',
        'f': 'geojson'
    }
    
    response = requests.get(query_url, params=params)
    
    if response.status_code != 200:
        print(f"Error fetching data: {response.status_code}")
        return None
    
    data = response.json()
    features = data.get('features', [])
    
    if not features:
        raise Exception("No features found for the specified query.")
    
    geometry = [shape(feature['geometry']) for feature in features]
    properties = [feature['properties'] for feature in features]
    gdf = gpd.GeoDataFrame(properties, geometry=geometry)
    return gdf

# Defining the function to download WorldPop data
def fetch_population_data(country: str, year: str):
    dataset_path = f"Global_2000_2020_Constrained/2020/BSGM/{country}/{country.lower()}_ppp_2020_UNadj_constrained.tif"
    download_url = f"{common.worldpop_url}{dataset_path}"
    try:
        response = requests.get(download_url)        
        if response.status_code != 200:
            print(f"Failed to fetch data. Status code: {response.status_code}")
            print(f"Response text: {response.text}")

        file_name = f"{DATA_DIR}/EXP/{country}_POP.tif"
        with open(file_name, 'wb') as file:
            file.write(response.content)
        print(f"Data downloaded successfully and saved as {file_name}")

    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")


def fetch_built_up_data(country: str):
    # Fetch the ADM data
    adm_data = get_adm_data(country, 0)  # Use ADM level 0 for country boundaries

    # Extract and combine the geometry into a single geometry
    ADM_area = adm_data.unary_union
    if not isinstance(ADM_area, (MultiPolygon, BaseGeometry)):
        ADM_area = MultiPolygon([ADM_area])

    # Convert to bounding box
    bbox = ADM_area.bounds

    # Construct the STAC search query
    search_query = {
        "bbox": list(bbox),
        "collections": ["WSF_2019"],
        "limit": 100
    }

    # Send the POST request to the STAC API
    headers = {"Content-Type": "application/json"}
    response = requests.post(common.stac_search_url, headers=headers, json=search_query)
    
    if response.status_code != 200:
        raise Exception(f"Error {response.status_code}: {response.text}")
        

    search_results = response.json()
    items = search_results.get("features", [])
    
    if items == []:
        print("No items found for the specified query.")
    
    print(f"Found {len(items)} items.")
    subfolder_name = f"{country}_tifs"
    download_folder = os.path.join(f"{DATA_DIR}/EXP/{country}_WSF_2019/", subfolder_name)
    if not os.path.exists(download_folder):
        os.makedirs(download_folder)

    tif_files = []
    total_files = len([asset for item in items for asset in item['assets'].values() if asset['href'].endswith('.tif')])
    
    with tqdm(total=total_files, desc="Downloading .tif files") as pbar:
        for item in items:
            for _, asset_value in item['assets'].items():
                if asset_value['href'].endswith('.tif'):
                    tif_file = download_file(asset_value['href'], download_folder)
                    tif_files.append(tif_file)
                    pbar.update(1)
                    
    merged_tif_path = os.path.join(download_folder, f"{subfolder_name}.tif")
    output_filename = os.path.join(f"{DATA_DIR}/EXP/{country}_WSF_2019/", f"{country}_WSF-2019.tif")
    if tif_files and not os.path.exists(output_filename):
        print("Mosaicing downloaded .tif files...")
        merge_tifs(download_folder)
        os.rename(merged_tif_path, output_filename)
    else:
        print("Mosaic already exists, skipping mosaicing.")  
        
    input_file = output_filename
    output_file = os.path.join(f"{DATA_DIR}/EXP/{country}_WSF_2019/", f"{country}_WSF-2019_100m.tif")
    output_calc_file = os.path.join(f"{DATA_DIR}/EXP/", f"{country}_BU.tif")
        
    if not os.path.exists(output_file):
        print("Resampling WSF 2019 to 100m...")
        gdalwarp_wsf19(input_file, output_file)
    else:
        print(f"{output_file} already exists, skipping upscaling.")
    
    if not os.path.exists(output_calc_file):
        print("Normalising WSF 2019 range [0 to 1]")
        gdal_calc_wsf19(output_file, output_calc_file)
        print(f"Mosaiced and Upscaled file saved as {output_calc_file}")
    else:
        print(f"{output_calc_file} already exists, skipping normalization.")

    if os.path.exists(download_folder):
        shutil.rmtree(download_folder)
        print(f"Deleted temporary folder: {download_folder}")


# Defining the function to download Agricultural data (TEMP, replace source)
def fetch_agri_data(country: str):
    dataset_path = f"Global_2000_2020_Constrained/2020/BSGM/{country}/{country.lower()}_ppp_2020_UNadj_constrained.tif"
    download_url = f"{common.worldpop_url}{dataset_path}"
    try:
        response = requests.get(download_url)
        if response.status_code != 200:
            print(f"Failed to fetch data. Status code: {response.status_code}")
            print(f"Response text: {response.text}")

        file_name = f"{DATA_DIR}/EXP/{country}_AGR.tif"
        with open(file_name, 'wb') as file:
            file.write(response.content)
        print(f"Data downloaded successfully and saved as {file_name}")

    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")


# Function to download files with progress bar
def download_file(url, dest_folder):
    if not os.path.exists(dest_folder):
        os.makedirs(dest_folder)

    local_filename = os.path.join(dest_folder, url.split('/')[-1])
    if os.path.exists(local_filename):
        return local_filename

    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    return local_filename


# Mosaic tiles
def merge_tifs(subdir_path):
    # Get a list of all .tif files in the subdirectory
    tif_files = [os.path.join(subdir_path, file) for file in os.listdir(subdir_path) if file.endswith('.tif')]
    
    # If there are .tif files in the subdirectory, merge them
    if tif_files:
        output_file = os.path.join(subdir_path, f"{os.path.basename(subdir_path)}.tif")
        vrt = gdal.BuildVRT('', tif_files)
        gdal.Translate(output_file, vrt, options='-co COMPRESS=DEFLATE -co PREDICTOR=2 -co ZLEVEL=9')
        vrt = None

# Resample WSF2019 from 10 to 100 meters
def gdalwarp_wsf19(input_file, output_file):
    warp_options = gdal.WarpOptions(
        format='GTiff',
        xRes=0.0008983152841195213,
        yRes=0.0008983152841195213,
        resampleAlg='average',
        multithread=True,
        creationOptions=[
            'COMPRESS=DEFLATE',
            'PREDICTOR=2',
            'ZLEVEL=9'
        ]
    )
    gdal.Warp(output_file, input_file, options=warp_options)

# Normalize WSF2019 as 0 to 1 range.
def gdal_calc_wsf19(input_file, output_file):
    # Open the input file
    ds = gdal.Open(input_file)
    band = ds.GetRasterBand(1)
    
    # Read the data into a numpy array
    data = band.ReadAsArray().astype(np.float32)
    
    # Perform the calculation
    result = data / 255.0
    
    # Create the output file
    driver = gdal.GetDriverByName('GTiff')
    out_ds = driver.Create(output_file, ds.RasterXSize, ds.RasterYSize, 1, gdal.GDT_Float32,
                           options=['COMPRESS=DEFLATE', 'PREDICTOR=2', 'ZLEVEL=9'])
    
    # Set the geotransform and projection
    out_ds.SetGeoTransform(ds.GetGeoTransform())
    out_ds.SetProjection(ds.GetProjection())
    
    # Write the data
    out_band = out_ds.GetRasterBand(1)
    out_band.WriteArray(result)
    
    # Close the datasets
    ds = None
    out_ds = None
