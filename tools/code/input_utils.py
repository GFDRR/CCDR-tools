# Check SSL limitations
import sys
sys.path.append('.')  # Ensure the current directory is in the path
try:
    from ssl_utils import disable_ssl_verification
    disable_ssl_verification()
except ImportError:
    import ssl
    import warnings
    import urllib3

    # Fallback if ssl_utils.py is not available
    warnings.filterwarnings('ignore', message='Unverified HTTPS request')
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    try:
        ssl._create_default_https_context = ssl._create_unverified_context
    except AttributeError:
        pass

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
    # The REST API is queried with f='geojson' above, and GeoJSON coordinates
    # are WGS84 (EPSG:4326) by spec - but without setting it explicitly here,
    # the returned GeoDataFrame's .crs was None. That's not just cosmetic: it
    # defeats any code (e.g. run_analysis's CRS reconciliation against the
    # exposure raster) that checks adm_data.crs to decide whether/how to
    # reproject - a None CRS was silently treated as "assume it already
    # matches", which is wrong whenever the raster ends up in a different
    # CRS (e.g. an antimeridian-crossing country's raster normalized into a
    # local projected CRS).
    gdf = gpd.GeoDataFrame(properties, geometry=geometry, crs='EPSG:4326')
    return gdf

# Defining the function to download WorldPop data
def fetch_population_data(country: str, year: str):
    if year != '2020':
        # The WorldPop "Constrained" mosaic used here is only published for 2020;
        # the dataset_path below is hardcoded to it. Previously the `year` argument
        # was silently ignored and 2020 data was fetched regardless of what was
        # requested, so callers requesting another year got wrong data with no
        # warning. Fail loudly instead until per-year fetching is implemented.
        print(f"ERROR: Population data fetch only supports year 2020 (requested: {year}). Skipping.")
        return

    dataset_path = f"Global_2000_2020_Constrained/2020/BSGM/{country}/{country.lower()}_ppp_2020_UNadj_constrained.tif"
    download_url = f"{common.worldpop_url}{dataset_path}"
    try:
        response = requests.get(download_url)
        if response.status_code != 200:
            print(f"Failed to fetch data. Status code: {response.status_code}")
            print(f"Response text: {response.text}")
            # Previously execution fell through and wrote this error response
            # body to the output .tif as if it were real data, then reported
            # success - silently corrupting the exposure input.
            return

        file_name = f"{DATA_DIR}/EXP/{country}_POP.tif"
        with open(file_name, 'wb') as file:
            file.write(response.content)
        print(f"Data downloaded successfully and saved as {file_name}")

        # WorldPop's own per-country rasters for antimeridian-straddling
        # countries (e.g. Fiji) are themselves published with a bounding box
        # spanning the full -180..180 longitude range - hundreds of thousands
        # of pixels wide, almost entirely nodata. See
        # get_country_antimeridian_info's docstring for the failure this
        # causes downstream if left as-is.
        crosses_antimeridian, country_geom = get_country_antimeridian_info(country)
        if crosses_antimeridian:
            print(f"Note: {country} crosses the antimeridian; normalizing "
                  f"population raster into a compact local projection...")
            raw_file = file_name + '.raw'
            os.replace(file_name, raw_file)
            try:
                normalize_antimeridian_raster(raw_file, country_geom, file_name)
            finally:
                os.remove(raw_file)

    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")


def get_country_antimeridian_info(country: str):
    """Determine whether a country's ADM0 boundary straddles the antimeridian
    (180 degree line), e.g. Fiji, whose islands are split between ~176-180 E
    (positive longitude) and just east of 180, which shapely/GeoJSON
    represent as negative longitude near -180.

    A single min/max bbox over such a geometry spans nearly the whole
    longitude range even though the real extent is only a few degrees wide -
    this is the shared root cause behind two separate problems: (1) a naive
    STAC bbox search finding only the tiles on one side of the dateline
    (missing e.g. Rotuma, Cikobia, the eastern Lau group), and (2) any
    per-country raster built or fetched with that -180..180 "bbox" ending up
    hundreds of thousands of pixels wide and almost entirely nodata - which
    in turn has caused native out-of-memory/allocation failures ("WinError
    87: the parameter is incorrect" on Windows) when the analysis tool loads
    the whole raster into memory.

    Returns
    -------
    (crosses, geometry) : crosses is True if the country straddles the
    antimeridian; geometry is the ADM0 union geometry in EPSG:4326.
    """
    adm_data = get_adm_data(country, 0)  # Use ADM level 0 for country boundaries
    ADM_area = adm_data.unary_union
    if not isinstance(ADM_area, (MultiPolygon, BaseGeometry)):
        ADM_area = MultiPolygon([ADM_area])

    parts = list(ADM_area.geoms) if hasattr(ADM_area, 'geoms') else [ADM_area]
    part_bounds = [part.bounds for part in parts]  # (minx, miny, maxx, maxy) each
    overall_minx = min(b[0] for b in part_bounds)
    overall_maxx = max(b[2] for b in part_bounds)
    crosses_antimeridian = (
        (overall_maxx - overall_minx) > 180
        and any(b[0] < 0 for b in part_bounds)
        and any(b[2] > 0 for b in part_bounds)
    )
    return crosses_antimeridian, ADM_area


# A local Mercator projection centered on longitude 180 - its own seam sits at
# the Greenwich meridian, nowhere near an antimeridian-crossing country's real
# territory, so tiles/rasters on both sides of the dateline become numerically
# contiguous instead of ~360 degrees apart.
ANTIMERIDIAN_LOCAL_CRS_PROJ4 = ('+proj=merc +lon_0=180 +k=1 +x_0=0 +y_0=0 '
                                 '+a=6378137 +b=6378137 +units=m +no_defs')


def normalize_antimeridian_raster(raster_path, country_geom_4326, output_path):
    """Reproject+crop a raster covering an antimeridian-crossing country from
    plain EPSG:4326 into the compact local Mercator CRS above.

    A country whose islands sit on both sides of the 180 degree line has an
    EPSG:4326 bounding box of roughly (-180, minlat, 180, maxlat) - the full
    range of longitude - even though its real extent is a few degrees wide.
    Third-party per-country rasters (e.g. WorldPop's own Fiji population
    layer) inherit this directly from the source; the result is a GeoTIFF
    hundreds of thousands of pixels wide, almost entirely nodata, which the
    rest of this tool cannot safely load into memory (see
    get_country_antimeridian_info's docstring for the observed failure mode).

    `cropToCutline` uses the country geometry's own extent (reprojected into
    the local CRS) to size the output raster, so the result is tight around
    the real data regardless of how wastefully wide the source raster is.

    The output is deliberately NOT reprojected back to EPSG:4326 afterwards -
    doing so re-wraps the coordinates through the dateline and reproduces the
    exact bug this function exists to avoid. The local Mercator CRS becomes
    this country's working CRS for the rest of the analysis: run_analysis
    reprojects the administrative boundaries to match whatever CRS the
    exposure raster ends up in, and calc_imp_RPs's WarpedVRT already
    reprojects the hazard raster the same way.
    """
    warp_kwargs = dict(
        dstSRS=ANTIMERIDIAN_LOCAL_CRS_PROJ4, format='GTiff',
        resampleAlg=gdal.GRA_NearestNeighbour, multithread=True,
        creationOptions=['COMPRESS=DEFLATE', 'PREDICTOR=2', 'ZLEVEL=9'],
    )
    if country_geom_4326 is not None:
        warp_kwargs.update(cutlineWKT=country_geom_4326.wkt, cutlineSRS='EPSG:4326', cropToCutline=True)
    result = gdal.Warp(output_path, raster_path, options=gdal.WarpOptions(**warp_kwargs))
    if result is None:
        raise RuntimeError(f"gdal.Warp failed to normalize antimeridian raster: {raster_path}")
    result = None


def fetch_built_up_data(country: str):
    crosses_antimeridian, ADM_area = get_country_antimeridian_info(country)
    parts = list(ADM_area.geoms) if hasattr(ADM_area, 'geoms') else [ADM_area]
    part_bounds = [part.bounds for part in parts]  # (minx, miny, maxx, maxy) each

    if crosses_antimeridian:
        west_bounds = [b for b in part_bounds if b[0] < 0]
        east_bounds = [b for b in part_bounds if b[2] >= 0]
        bboxes = []
        if west_bounds:
            bboxes.append([min(b[0] for b in west_bounds), min(b[1] for b in west_bounds),
                            max(b[2] for b in west_bounds), max(b[3] for b in west_bounds)])
        if east_bounds:
            bboxes.append([min(b[0] for b in east_bounds), min(b[1] for b in east_bounds),
                            max(b[2] for b in east_bounds), max(b[3] for b in east_bounds)])
        print(f"Note: {country} geometry appears to cross the antimeridian; "
              f"querying {len(bboxes)} separate bounding boxes instead of one.")
    else:
        bboxes = [list(ADM_area.bounds)]

    # Send one POST request per bounding box to the STAC API, combining results
    headers = {"Content-Type": "application/json"}
    items = []
    seen_ids = set()
    for bbox in bboxes:
        search_query = {
            "bbox": bbox,
            "collections": ["WSF_2019"],
            "limit": 100
        }
        response = requests.post(common.stac_search_url, headers=headers, json=search_query)

        if response.status_code != 200:
            raise Exception(f"Error {response.status_code}: {response.text}")

        search_results = response.json()
        for item in search_results.get("features", []):
            item_id = item.get("id")
            if item_id is None or item_id not in seen_ids:
                if item_id is not None:
                    seen_ids.add(item_id)
                items.append(item)

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
    # NOTE: this still fetches WorldPop POPULATION data (same dataset_path as
    # fetch_population_data), saved under an "_AGR" filename - flagged as TEMP in
    # the original comment above, kept as-is here since no real agricultural
    # exposure source has been wired in yet. Confirm this is still intentional
    # before relying on AGR outputs.
    dataset_path = f"Global_2000_2020_Constrained/2020/BSGM/{country}/{country.lower()}_ppp_2020_UNadj_constrained.tif"
    download_url = f"{common.worldpop_url}{dataset_path}"
    try:
        response = requests.get(download_url)
        if response.status_code != 200:
            print(f"Failed to fetch data. Status code: {response.status_code}")
            print(f"Response text: {response.text}")
            # See fetch_population_data: previously fell through and wrote the
            # error response body to the output .tif as if it were real data.
            return

        file_name = f"{DATA_DIR}/EXP/{country}_AGR.tif"
        with open(file_name, 'wb') as file:
            file.write(response.content)
        print(f"Data downloaded successfully and saved as {file_name}")

        # See fetch_population_data: WorldPop's own per-country rasters for
        # antimeridian-straddling countries are published spanning the full
        # -180..180 longitude range.
        crosses_antimeridian, country_geom = get_country_antimeridian_info(country)
        if crosses_antimeridian:
            print(f"Note: {country} crosses the antimeridian; normalizing "
                  f"agriculture raster into a compact local projection...")
            raw_file = file_name + '.raw'
            os.replace(file_name, raw_file)
            try:
                normalize_antimeridian_raster(raw_file, country_geom, file_name)
            finally:
                os.remove(raw_file)

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


def _get_tif_lon_bounds(path):
    """Return (minx, maxx) longitude bounds of a GeoTIFF, assuming a
    geographic (lon/lat) CRS - true for the WSF_2019 tiles this is used on."""
    ds = gdal.Open(path)
    gt = ds.GetGeoTransform()
    minx = gt[0]
    maxx = minx + gt[1] * ds.RasterXSize
    ds = None
    return min(minx, maxx), max(minx, maxx)


def _tiles_cross_antimeridian(tif_files):
    """Detect whether a set of tiles collectively straddle the 180 degree
    line - some tiles at high positive longitude, others wrapped to high
    negative longitude (e.g. Fiji's WSF_2019 tiles split between ~176-180E
    and, wrapped, just east of 180 as negative longitude)."""
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
    reprojected back to EPSG:4326. An earlier version of this function did
    reproject back to EPSG:4326 for consistency with the rest of the tool's
    degree-based pipeline - but that re-wraps the coordinates through the
    dateline and reproduces the exact "bounding box spans the whole globe"
    problem this function exists to avoid (confirmed against Fiji's real
    tiles: the round-tripped file had the same ~-180..180 extent as the
    naive, non-antimeridian-aware merge it was meant to replace). Downstream
    steps (gdalwarp_wsf19, run_analysis's CRS reconciliation) now detect and
    handle a projected (meters) input instead of assuming degrees.

    Adapted from a one-off fix originally applied by hand for Fiji's WSF_2019
    tiles (a separate, non-automatic script) - generalized here to trigger
    automatically for any antimeridian-crossing country instead of requiring a
    manual swap-in each time.
    """
    temp_dir = os.path.join(os.path.dirname(output_file),
                             f"{os.path.basename(output_file)}_antimeridian_tmp")
    os.makedirs(temp_dir, exist_ok=True)

    try:
        reprojected_files = []
        for tif_file in tif_files:
            out_name = os.path.join(temp_dir, f"reprojected_{os.path.basename(tif_file)}")
            src_ds = gdal.Open(tif_file)
            if src_ds is None:
                print(f"Warning: could not open {tif_file} for antimeridian-safe merge, skipping.")
                continue
            gdal.Warp(out_name, src_ds, options=gdal.WarpOptions(
                dstSRS=ANTIMERIDIAN_LOCAL_CRS_PROJ4, format='GTiff',
                resampleAlg=gdal.GRA_NearestNeighbour, multithread=True,
            ))
            src_ds = None
            reprojected_files.append(out_name)

        if not reprojected_files:
            print(f"Warning: no tiles could be reprojected for antimeridian-safe merge of {output_file}.")
            return

        vrt = gdal.BuildVRT('', reprojected_files, options=gdal.BuildVRTOptions(resampleAlg='near'))
        gdal.Translate(output_file, vrt, options=gdal.TranslateOptions(
            creationOptions=['COMPRESS=DEFLATE', 'PREDICTOR=2', 'ZLEVEL=9']
        ))
        vrt = None
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


# Mosaic tiles
def merge_tifs(subdir_path):
    # Get a list of all .tif files in the subdirectory
    tif_files = [os.path.join(subdir_path, file) for file in os.listdir(subdir_path) if file.endswith('.tif')]

    # If there are .tif files in the subdirectory, merge them
    if tif_files:
        output_file = os.path.join(subdir_path, f"{os.path.basename(subdir_path)}.tif")
        if _tiles_cross_antimeridian(tif_files):
            # A plain BuildVRT/Translate in lon/lat coordinates cannot
            # correctly place tiles that are numerically split across +180
            # and -180 - it would treat them as ~360 degrees apart instead of
            # adjacent, corrupting the mosaic (this is exactly the gap that
            # required a one-off manual fix for Fiji's built-up exposure tiles
            # previously; fetch_built_up_data's bbox search alone finds tiles
            # on both sides of the dateline, but this merge step still needs
            # to handle stitching them together correctly).
            print(f"Note: tiles in {subdir_path} appear to cross the antimeridian; "
                  f"merging via a longitude-180-centered projection to avoid "
                  f"dateline mosaic misalignment.")
            _merge_tifs_across_antimeridian(tif_files, output_file)
        else:
            vrt = gdal.BuildVRT('', tif_files)
            gdal.Translate(output_file, vrt, options='-co COMPRESS=DEFLATE -co PREDICTOR=2 -co ZLEVEL=9')
            vrt = None

# Resample WSF2019 from 10 to 100 meters
def gdalwarp_wsf19(input_file, output_file):
    # 0.0008983152841195213 degrees is ~100m at the equator - only meaningful
    # for a geographic (degree) CRS. An antimeridian-crossing country's merged
    # mosaic is now left in a local Mercator CRS (meters, see
    # _merge_tifs_across_antimeridian), so the equivalent target resolution
    # there is simply 100 map units = 100m.
    src_ds = gdal.Open(input_file)
    is_geographic = src_ds.GetSpatialRef().IsGeographic()
    src_ds = None
    target_res = 0.0008983152841195213 if is_geographic else 100.0

    warp_options = gdal.WarpOptions(
        format='GTiff',
        xRes=target_res,
        yRes=target_res,
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
