import geopandas as gpd
import numpy as np
import os
from osgeo import gdal
import requests
from shapely.geometry import shape

import common

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
    
    
def read_first_band(ds):
    band = ds.GetRasterBand(1)
    data = band.ReadAsArray().astype(np.float)
    return data
    

def gdal_ds_is_normalized(file_path: str):
    
    with gdal.Open(file_path) as ds:
        if ds is None:
            return False
        
        data = read_first_band(ds)
                
        return (np.min(data >= 0.0 and np.max(data) <= 1.0))
    
    
def gdal_calc_wsf19(input_file, output_file):
    
    gdal.UseExceptions()
    
    if os.path.exists(output_file) and gdal_ds_is_normalized(output_file):
        print(f"Output file '{output_file}' already exists and is normalized.")
        return 
    
    with gdal.Open(input_file) as ds:
        if ds is None:
            FileNotFoundError(f"Cannot open input file: {input_file}")
        
        # Read first band into a numpy array
        data = read_first_band(ds)
        
        normalized_data = data / 255.0
        
        driver = gdal.GetDriverByName('GTiff')
        with driver.Create(output_file, ds.RasterXSize, ds.RasterYSize, 1, gdal.GDT_Float32,
                           options=['COMPRESS=DEFLAT', 'PREDICTOR=2', 'ZLEVEL=9']) as out_ds:
            
            if out_ds is None:
                raise RuntimeError(f"Failed to create output file: {output_file}.")
            
            # Set geotransforms and projection
            out_ds.SetGeoTransform(ds.GetGeoTransform())
            out_ds.SetProject(ds.GetProjection())
            
            # Write the normalized data to the output file
            out_band = out_ds.GetRasterBand(1)
            out_band.WriteArray(normalized_data)
            
            # Flush cache to ensure all data is written
            out_band.FlushCache()


# Function to get the correct layer ID based on administrative level
def get_layer_id_for_adm(adm_level):
    layers_url = f"{common.rest_api_url}/layers"
    target_layer_name = f"WB_GAD_ADM{adm_level}"

    response = requests.get(layers_url, params={'f': 'json'})
    
    if response.status_code != 200:
        print(f"Failed to fetch layers. Status code: {response.status_code}")
        return None

    layers_info = response.json().get('layers', [])
    
    for layer in layers_info:
        if layer['name'] == target_layer_name:
            return layer['id']
    
    print(f"Layer matching {target_layer_name} not found.")
    return None


# Function to fetch the ADM data using the correct layer ID
def get_adm_data(country, adm_level):
    layer_id = get_layer_id_for_adm(adm_level)
    
    if not layer_id:
        print("Invalid administrative level or layer mapping not found.")
        return None
    
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
        print("No features found for the specified query.")
        return None
    
    geometry = [shape(feature['geometry']) for feature in features]
    properties = [feature['properties'] for feature in features]
    gdf = gpd.GeoDataFrame(properties, geometry=geometry)
    return gdf


# Defining the function to download WorldPop data
def fetch_population_data(country: str, exp_year: str, data_dir: str): 
    
    dataset_path = f"Global_2000_2020_Constrained/{exp_year}/BSGM/{country}/{country.lower()}_ppp_{exp_year}_UNadj_constrained.tif"
    download_url = f"{common.worldpop_url}{dataset_path}"
    
    file_name = f"{data_dir}/EXP/{country}_POP{exp_year}.tif"
    
    if os.path.exists(file_name):
        print(f"File name '{file_name}' exists already. Skipping download...")
        return 

    try:
        response = requests.get(download_url)
        
        if response.status_code != 200:
            print(f"Failed to fetch data. Status code: {response.status_code}")
            print(f"Response text: {response.text}")

        with open(file_name, 'wb') as file:
            file.write(response.content)
        print(f"Data downloaded successfully and saved as {file_name}")

    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")    
             
        
def save_geopackage(result_df, country, adm_level, haz_cat, exp_cat, exp_year, analysis_type, valid_RPs):
    # Ensure that the geometry column is correctly recognized
    result_df = result_df.rename(columns={'geom': 'geometry'})
    if 'geometry' not in result_df.columns:
        raise ValueError("The DataFrame does not contain a geometry column.")
   
    # Convert to GeoDataFrame if it's not already one
    if not isinstance(result_df, gpd.GeoDataFrame):
        result_df = gpd.GeoDataFrame(result_df, geometry='geometry')
   
    # Set the CRS to EPSG:4326
    result_df.set_crs(epsg=4326, inplace=True)
   
    # Remove the geometry column for the CSV export
    no_geom = result_df.drop(columns=['geometry'], errors='ignore').fillna(0)
       
    file_prefix = f"{country}_ADM{adm_level}_{haz_cat}_{exp_cat}_{exp_year}"

    if analysis_type == "Function":
        EAI_string = "EAI_" if len(valid_RPs) > 1 else ""
        no_geom.to_csv(os.path.join(common.OUTPUT_DIR, f"{file_prefix}_{EAI_string}function.csv"), index=False)
        result_df.to_file(os.path.join(common.OUTPUT_DIR, f"{file_prefix}_{EAI_string}function.gpkg"), driver='GPKG')
    elif analysis_type == "Classes":
        EAE_string = "EAE_" if len(valid_RPs) > 1 else ""
        no_geom.to_csv(os.path.join(common.OUTPUT_DIR, f"{file_prefix}_{EAE_string}class.csv"), index=False)
        result_df.to_file(os.path.join(common.OUTPUT_DIR, f"{file_prefix}_{EAE_string}class.gpkg"), driver='GPKG')
    else:
        raise ValueError("Unknown analysis type. Use 'Function' or 'Classes'.")
    
    return result_df  # Return the GeoDataFrame