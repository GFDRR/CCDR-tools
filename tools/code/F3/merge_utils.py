import os
import numpy as np
from osgeo import gdal

def merge_tifs(subdir_path):
    # Get a list of all .tif files in the subdirectory
    tif_files = [os.path.join(subdir_path, file) for file in os.listdir(subdir_path) if file.endswith('.tif')]

    # If there are .tif files in the subdirectory, merge them
    if tif_files:
        # Change the output file path to be one directory up
        parent_dir = os.path.dirname(subdir_path)
        output_file = os.path.join(parent_dir, f"{os.path.basename(subdir_path)}.tif")

        # Step 1: Build VRT and merge tiles into temporary file
        temp_output = output_file + '.tmp.tif'
        vrt = gdal.BuildVRT('', tif_files)
        gdal.Translate(temp_output, vrt, options='-co COMPRESS=DEFLATE -co PREDICTOR=2 -co ZLEVEL=9')
        vrt = None

        # Step 2: Process the merged file to convert negatives to 0 and set nodata=0
        print(f"Processing {os.path.basename(subdir_path)}: converting negative values to 0 and setting nodata=0")

        # Open the temporary file
        src_ds = gdal.Open(temp_output, gdal.GA_ReadOnly)
        if src_ds is None:
            print(f"Error: Could not open {temp_output}")
            return

        # Get raster properties
        driver = gdal.GetDriverByName('GTiff')
        cols = src_ds.RasterXSize
        rows = src_ds.RasterYSize
        bands = src_ds.RasterCount
        projection = src_ds.GetProjection()
        geotransform = src_ds.GetGeoTransform()

        # Create output file with nodata=0
        dst_ds = driver.Create(output_file, cols, rows, bands, gdal.GDT_Float32,
                              options=['COMPRESS=DEFLATE', 'PREDICTOR=2', 'ZLEVEL=9'])
        dst_ds.SetProjection(projection)
        dst_ds.SetGeoTransform(geotransform)

        # Process each band
        for band_idx in range(1, bands + 1):
            src_band = src_ds.GetRasterBand(band_idx)
            data = src_band.ReadAsArray()

            # Convert negative values to 0
            data = np.where(data < 0, 0, data)

            # Write processed data to output
            dst_band = dst_ds.GetRasterBand(band_idx)
            dst_band.WriteArray(data)
            dst_band.SetNoDataValue(0)  # Set 0 as nodata
            dst_band.FlushCache()

        # Close datasets
        src_ds = None
        dst_ds = None

        # Remove temporary file
        try:
            os.remove(temp_output)
        except Exception as e:
            print(f"Warning: Could not remove temporary file {temp_output}: {e}")

        print(f"Completed {os.path.basename(subdir_path)}: output saved to {output_file}")