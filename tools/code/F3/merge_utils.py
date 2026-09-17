import os
import shutil
import numpy as np
from osgeo import gdal


def _get_tif_lon_bounds(path):
    """Return (minx, maxx) longitude bounds of a GeoTIFF, assuming a
    geographic (lon/lat) CRS - true for the Fathom tiles this is used on."""
    ds = gdal.Open(path)
    gt = ds.GetGeoTransform()
    minx = gt[0]
    maxx = minx + gt[1] * ds.RasterXSize
    ds = None
    return min(minx, maxx), max(minx, maxx)


def _tiles_cross_antimeridian(tif_files):
    """Detect whether a set of tiles collectively straddle the 180 degree
    line - some tiles at high positive longitude, others wrapped to high
    negative longitude (e.g. Fiji's tiles split between ~176-180E and,
    wrapped, just east of 180 as negative longitude)."""
    bounds = [_get_tif_lon_bounds(f) for f in tif_files]
    overall_minx = min(b[0] for b in bounds)
    overall_maxx = max(b[1] for b in bounds)
    return (
        (overall_maxx - overall_minx) > 180
        and any(b[0] < 0 for b in bounds)
        and any(b[1] > 0 for b in bounds)
    )


def _merge_tifs_across_antimeridian(tif_files, output_file):
    """
    Merge tiles that straddle the antimeridian (180 degree line) by
    reprojecting each tile to a Mercator projection centered on longitude 180
    (moving the projection's discontinuity to the Greenwich meridian, far from
    the data) and merging in that projection, where there's no dateline
    wraparound.

    The merged output is deliberately LEFT in this local Mercator CRS, not
    reprojected back to EPSG:4326. An earlier version of this function (and,
    separately, the near-identical one in input_utils.py for exposure tiles)
    did reproject back to EPSG:4326 - but that re-wraps the coordinates
    through the dateline and reproduces the exact "spans the whole globe"
    problem this function exists to avoid. This is safe to leave un-reprojected:
    calc_imp_RPs's WarpedVRT already reads a hazard raster's own CRS and warps
    it on the fly to match the exposure raster's CRS, whatever that is.

    Adapted from a one-off fix originally applied by hand for Fiji (a separate,
    non-automatic script/notebook) - generalized here to trigger automatically
    for any antimeridian-crossing country instead of requiring a manual
    swap-in each time.
    """
    temp_dir = os.path.join(os.path.dirname(output_file),
                             f"{os.path.basename(output_file)}_antimeridian_tmp")
    os.makedirs(temp_dir, exist_ok=True)

    # A generic longitude-180-centered Mercator - the seam sits at longitude 0,
    # nowhere near an antimeridian-crossing country's own tiles.
    custom_proj = ('+proj=merc +lon_0=180 +k=1 +x_0=0 +y_0=0 +a=6378137 +b=6378137 '
                   '+towgs84=0,0,0,0,0,0,0 +units=m +no_defs')

    try:
        reprojected_files = []
        for tif_file in tif_files:
            out_name = os.path.join(temp_dir, f"reprojected_{os.path.basename(tif_file)}")
            src_ds = gdal.Open(tif_file)
            if src_ds is None:
                print(f"Warning: could not open {tif_file} for antimeridian-safe merge, skipping.")
                continue
            gdal.Warp(out_name, src_ds, options=gdal.WarpOptions(
                dstSRS=custom_proj, format='GTiff',
                resampleAlg=gdal.GRA_NearestNeighbour, multithread=True,
            ))
            src_ds = None
            reprojected_files.append(out_name)

        if not reprojected_files:
            print(f"Warning: no tiles could be reprojected for antimeridian-safe merge of {output_file}.")
            return

        # NearestNeighbour throughout preserves Fathom's exact sentinel values
        # (-32767 permanent water, -32768 nodata) without interpolation
        # smearing them into neighbouring depth values.
        vrt = gdal.BuildVRT('', reprojected_files, options=gdal.BuildVRTOptions(resampleAlg='near'))
        gdal.Translate(output_file, vrt, options=gdal.TranslateOptions(
            creationOptions=['COMPRESS=DEFLATE', 'PREDICTOR=2', 'ZLEVEL=9']
        ))
        vrt = None
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def merge_tifs(subdir_path):
    """
    Merge Fathom 3 tiles into a single raster.

    Properly handles Fathom 3 data encoding:
    - Values 0-1,000: Valid flood depths in centimetres
    - Value -32,767: Permanent water bodies
    - Value -32,768: NoData sentinel
    - Preserves all negative values as-is (no conversion)

    Tiles that collectively straddle the antimeridian (180 degree line) are
    merged via a longitude-180-centered projection to avoid dateline mosaic
    misalignment (a plain BuildVRT/Translate in lon/lat coordinates cannot
    correctly place tiles that are numerically split across +180 and -180 -
    it would treat them as ~360 degrees apart instead of adjacent). The
    merged result stays in that local projected CRS (see
    _merge_tifs_across_antimeridian) rather than being reprojected back to
    EPSG:4326, before the nodata standardization step below runs as usual.
    """
    # Get a list of all .tif files in the subdirectory
    tif_files = [os.path.join(subdir_path, file) for file in os.listdir(subdir_path) if file.endswith('.tif')]

    # If there are .tif files in the subdirectory, merge them
    if tif_files:
        # Change the output file path to be one directory up
        parent_dir = os.path.dirname(subdir_path)
        output_file = os.path.join(parent_dir, f"{os.path.basename(subdir_path)}.tif")

        # Step 1: Build VRT and merge tiles into temporary file
        temp_output = output_file + '.tmp.tif'
        if _tiles_cross_antimeridian(tif_files):
            print(f"Note: tiles in {subdir_path} appear to cross the antimeridian; "
                  f"merging via a longitude-180-centered projection to avoid "
                  f"dateline mosaic misalignment.")
            _merge_tifs_across_antimeridian(tif_files, temp_output)
        else:
            vrt = gdal.BuildVRT('', tif_files)
            gdal.Translate(temp_output, vrt, options='-co COMPRESS=DEFLATE -co PREDICTOR=2 -co ZLEVEL=9')
            vrt = None

        # Step 2: Process the merged file to set consistent nodata=-32768
        print(f"Processing {os.path.basename(subdir_path)}: setting nodata=-32768 (Fathom standard)")

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
        data_type = src_ds.GetRasterBand(1).DataType  # Get data type from source

        # Create output file with nodata=-32768
        dst_ds = driver.Create(output_file, cols, rows, bands, data_type,
                              options=['COMPRESS=DEFLATE', 'PREDICTOR=2', 'ZLEVEL=9'])
        dst_ds.SetProjection(projection)
        dst_ds.SetGeoTransform(geotransform)

        # Process each band
        for band_idx in range(1, bands + 1):
            src_band = src_ds.GetRasterBand(band_idx)
            data = src_band.ReadAsArray()

            # Get the source nodata value
            src_nodata = src_band.GetNoDataValue()

            # Replace source nodata with -32768 (Fathom standard NoData sentinel)
            # This ensures consistent nodata across all tiles
            if src_nodata is not None and src_nodata != -32768:
                data = np.where(data == src_nodata, -32768, data)

            # IMPORTANT: Do NOT modify other negative values
            # -32767 is permanent water (valid data)
            # All negative values except nodata are meaningful in Fathom data
            # Zero is valid (dry land), not nodata

            # Write processed data to output
            dst_band = dst_ds.GetRasterBand(band_idx)
            dst_band.WriteArray(data)
            dst_band.SetNoDataValue(-32768)  # Set -32768 as nodata (Fathom standard)
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