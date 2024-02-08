import os
from osgeo import gdal

def merge_tifs(subdir_path):
    # Get a list of all .tif files in the subdirectory
    tif_files = [os.path.join(subdir_path, file) for file in os.listdir(subdir_path) if file.endswith('.tif')]
    
    # If there are .tif files in the subdirectory, merge them
    if tif_files:
        output_file = os.path.join(subdir_path, f"{os.path.basename(subdir_path)}.tif")
        vrt = gdal.BuildVRT('', tif_files)
        gdal.Translate(output_file, vrt, options='-co COMPRESS=DEFLATE -co PREDICTOR=2 -co ZLEVEL=9')
        vrt = None
