import os
from osgeo import gdal
import numpy as np

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
