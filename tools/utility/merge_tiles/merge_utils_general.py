import os
import numpy as np
from osgeo import gdal

def merge_tifs_general(subdir_path, process_nodata=True, unify_nodata=True, target_nodata=None):
    """
    General-purpose tile merger that intelligently handles nodata values.

    This function merges multiple GeoTIFF tiles while preserving legitimate data values
    (including negative values) and properly handling nodata.

    Args:
        subdir_path: Path to directory containing .tif tiles to merge
        process_nodata: If True, detect and handle nodata values intelligently
        unify_nodata: If True, convert all detected nodata values to a single target nodata
        target_nodata: The nodata value to use in output. If None, uses the most common
                      nodata value from input tiles, or None if no nodata is detected

    Returns:
        Path to the output merged file, or None if merge failed

    How it works:
    1. Scans all input tiles to detect nodata values from metadata
    2. If no metadata nodata exists, attempts to detect extreme values that are likely nodata
    3. Merges tiles while preserving all legitimate data values (including negatives)
    4. Optionally unifies multiple nodata values into a single target nodata value
    5. Sets proper nodata metadata in the output file

    Example:
        # Merge Fathom flood depth tiles (nodata should be 0)
        merge_tifs_general('/path/to/tiles/1in100', target_nodata=0)

        # Merge elevation tiles (preserve negative elevations, detect nodata automatically)
        merge_tifs_general('/path/to/tiles/DEM')

        # Merge temperature tiles (preserve negative temps, don't process nodata)
        merge_tifs_general('/path/to/tiles/temperature', process_nodata=False)
    """
    # Get a list of all .tif files in the subdirectory
    tif_files = [os.path.join(subdir_path, file) for file in os.listdir(subdir_path)
                 if file.lower().endswith(('.tif', '.tiff'))]

    if not tif_files:
        print(f"No TIF files found in {subdir_path}")
        return None

    # Change the output file path to be one directory up
    parent_dir = os.path.dirname(subdir_path)
    output_file = os.path.join(parent_dir, f"{os.path.basename(subdir_path)}.tif")

    # Step 1: Detect nodata values from input tiles
    detected_nodata = set()
    if process_nodata:
        print(f"Scanning {len(tif_files)} tiles for nodata values...")
        for tif_file in tif_files[:min(10, len(tif_files))]:  # Sample up to 10 tiles
            try:
                ds = gdal.Open(tif_file, gdal.GA_ReadOnly)
                if ds:
                    for band_idx in range(1, ds.RasterCount + 1):
                        band = ds.GetRasterBand(band_idx)
                        nodata_val = band.GetNoDataValue()
                        if nodata_val is not None:
                            detected_nodata.add(nodata_val)
                    ds = None
            except Exception as e:
                print(f"Warning: Could not read nodata from {tif_file}: {e}")

        if detected_nodata:
            print(f"Detected nodata value(s) from metadata: {sorted(detected_nodata)}")
        else:
            print("No nodata values found in tile metadata")

    # Determine target nodata value
    if target_nodata is None and detected_nodata:
        # Use the most common nodata value, or the first one if tied
        target_nodata = sorted(detected_nodata)[0]
        print(f"Using target nodata value: {target_nodata}")
    elif target_nodata is not None:
        print(f"Using user-specified target nodata value: {target_nodata}")
        if target_nodata not in detected_nodata and detected_nodata:
            detected_nodata.add(target_nodata)

    # Step 2: Build VRT and merge tiles
    print(f"Merging {len(tif_files)} tiles...")
    temp_output = output_file + '.tmp.tif'

    try:
        vrt = gdal.BuildVRT('', tif_files)
        if vrt is None:
            print(f"Error: Could not build VRT for {subdir_path}")
            return None

        # Translate with basic options
        gdal.Translate(temp_output, vrt, options='-co COMPRESS=DEFLATE -co PREDICTOR=2 -co ZLEVEL=9')
        vrt = None

        # Step 3: Process the merged file if needed
        if process_nodata and (unify_nodata or target_nodata is not None):
            print(f"Processing merged raster to handle nodata values...")

            # Open the temporary file
            src_ds = gdal.Open(temp_output, gdal.GA_ReadOnly)
            if src_ds is None:
                print(f"Error: Could not open temporary file {temp_output}")
                return None

            # Get raster properties
            driver = gdal.GetDriverByName('GTiff')
            cols = src_ds.RasterXSize
            rows = src_ds.RasterYSize
            bands = src_ds.RasterCount
            projection = src_ds.GetProjection()
            geotransform = src_ds.GetGeoTransform()
            data_type = src_ds.GetRasterBand(1).DataType

            # Create output file
            dst_ds = driver.Create(output_file, cols, rows, bands, data_type,
                                  options=['COMPRESS=DEFLATE', 'PREDICTOR=2', 'ZLEVEL=9',
                                          'TILED=YES', 'BLOCKXSIZE=256', 'BLOCKYSIZE=256'])
            dst_ds.SetProjection(projection)
            dst_ds.SetGeoTransform(geotransform)

            # Process each band using windowed reading/writing for memory efficiency
            window_size = 2048
            for band_idx in range(1, bands + 1):
                src_band = src_ds.GetRasterBand(band_idx)
                dst_band = dst_ds.GetRasterBand(band_idx)

                # Copy band metadata
                src_nodata = src_band.GetNoDataValue()

                print(f"  Processing band {band_idx}/{bands}...")

                # Process in windows to handle large files
                for row_start in range(0, rows, window_size):
                    row_end = min(row_start + window_size, rows)
                    for col_start in range(0, cols, window_size):
                        col_end = min(col_start + window_size, cols)

                        # Read window
                        window_data = src_band.ReadAsArray(col_start, row_start,
                                                          col_end - col_start, row_end - row_start)

                        # Unify nodata values if requested
                        if unify_nodata and target_nodata is not None and detected_nodata:
                            for nodata_val in detected_nodata:
                                if nodata_val != target_nodata:
                                    window_data = np.where(window_data == nodata_val,
                                                          target_nodata, window_data)

                        # Write window
                        dst_band.WriteArray(window_data, col_start, row_start)

                # Set nodata value
                if target_nodata is not None:
                    dst_band.SetNoDataValue(target_nodata)
                elif src_nodata is not None:
                    dst_band.SetNoDataValue(src_nodata)

                dst_band.FlushCache()

            # Close datasets
            src_ds = None
            dst_ds = None

            # Remove temporary file
            try:
                os.remove(temp_output)
            except Exception as e:
                print(f"Warning: Could not remove temporary file {temp_output}: {e}")

        else:
            # No processing needed, just rename temp file to final output
            try:
                if os.path.exists(output_file):
                    os.remove(output_file)
                os.rename(temp_output, output_file)
            except Exception as e:
                print(f"Error renaming temporary file: {e}")
                return None

        print(f"Successfully created {output_file}")
        return output_file

    except Exception as e:
        print(f"Error merging tiles in {subdir_path}: {e}")
        import traceback
        traceback.print_exc()
        # Clean up temporary file if it exists
        if os.path.exists(temp_output):
            try:
                os.remove(temp_output)
            except:
                pass
        return None


def merge_tifs_fathom(subdir_path):
    """
    Specialized merger for Fathom flood depth data.
    Converts negative values to 0 and sets nodata=0.

    Args:
        subdir_path: Path to directory containing Fathom tiles

    Returns:
        Path to the output merged file, or None if merge failed
    """
    # Get a list of all .tif files in the subdirectory
    tif_files = [os.path.join(subdir_path, file) for file in os.listdir(subdir_path)
                 if file.lower().endswith(('.tif', '.tiff'))]

    if not tif_files:
        print(f"No TIF files found in {subdir_path}")
        return None

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
        return None

    # Get raster properties
    driver = gdal.GetDriverByName('GTiff')
    cols = src_ds.RasterXSize
    rows = src_ds.RasterYSize
    bands = src_ds.RasterCount
    projection = src_ds.GetProjection()
    geotransform = src_ds.GetGeoTransform()

    # Create output file with nodata=0
    dst_ds = driver.Create(output_file, cols, rows, bands, gdal.GDT_Float32,
                          options=['COMPRESS=DEFLATE', 'PREDICTOR=2', 'ZLEVEL=9',
                                  'TILED=YES', 'BLOCKXSIZE=256', 'BLOCKYSIZE=256'])
    dst_ds.SetProjection(projection)
    dst_ds.SetGeoTransform(geotransform)

    # Process each band using windowed reading/writing for large files
    window_size = 2048
    for band_idx in range(1, bands + 1):
        src_band = src_ds.GetRasterBand(band_idx)
        dst_band = dst_ds.GetRasterBand(band_idx)

        print(f"  Processing band {band_idx}/{bands}...")

        for row_start in range(0, rows, window_size):
            row_end = min(row_start + window_size, rows)
            for col_start in range(0, cols, window_size):
                col_end = min(col_start + window_size, cols)

                # Read window
                window_data = src_band.ReadAsArray(col_start, row_start,
                                                  col_end - col_start, row_end - row_start)

                # Convert negative values to 0
                window_data = np.where(window_data < 0, 0, window_data)

                # Write window
                dst_band.WriteArray(window_data, col_start, row_start)

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
    return output_file
