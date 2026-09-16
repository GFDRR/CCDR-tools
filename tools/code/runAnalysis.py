# Required libraries
import os, gc
import datetime
import traceback
# Force openpyxl to use the pure-Python stdlib XML implementation instead of
# lxml. Root-caused via a full Windows crash dump (WinDbg !analyze -v): a
# reproducible, intermittent access violation inside libxml2's xmlDictReference
# (lxml's etree C extension), a critical-section/reference-counting corruption
# in libxml2 itself - not GDAL, not numpy, not this project's own code. This
# must be set before openpyxl is imported anywhere in the process (it reads
# this env var once, at import time, into a module-level flag).
os.environ.setdefault('OPENPYXL_LXML', 'False')
import warnings
import numpy as np
import pandas as pd
import geopandas as gpd
import folium
from branca.colormap import LinearColormap
from openpyxl import load_workbook
import rasterio
import rioxarray as rxr
from rasterstats import gen_zonal_stats, zonal_stats
import xarray as xr

# Importing internal libraries
import common
import input_utils
from damageFunctions import FL_mortality_factor, FL_damage_factor_builtup, FL_damage_factor_agri, TC_damage_factor_builtup 

# Importing the libraries for parallel processing
import itertools as it
from functools import partial
import multiprocess as mp
import dask.array as da
import dask

# Configure dask for better memory management
dask.config.set({
    'array.chunk-size': '1GB',
    'array.slicing.split_large_chunks': True,
    'temporary-directory': None  # Use system temp directory
})

DATA_DIR = common.DATA_DIR
OUTPUT_DIR = common.OUTPUT_DIR
warnings.filterwarnings("ignore", message="'GeoSeries.swapaxes' is deprecated", category=FutureWarning)

# Defining functions for parallel processing of zonal_stats
def chunks(iterable_data, n):
    it_data = iter(iterable_data)
    for chunk in iter(lambda: list(it.islice(it_data, n)), []):
        yield chunk

def zonal_stats_partial(feats, raster, stats="*", affine=None, nodata=None, all_touched=True):
    # Partial zonal stats for parallel processing on a list of features
    return zonal_stats(feats, raster, stats=stats, affine=affine, nodata=nodata, all_touched=all_touched)

def zonal_stats_parallel(args):
    # Zonal stats for a parallel processing on a list of features
    return zonal_stats_partial(*args)

def save_excel_file(excel_file, dataset, sheet_name, summary_sheet=False):

    summary_exists = False
    file_is_valid_existing = False

    if os.path.exists(excel_file):
        try:
            # read_only workbooks keep the underlying file handle open until
            # .close() is called explicitly - relying on garbage collection
            # left the handle open for the life of the process, which on
            # Windows blocked moving/editing/deleting the xlsx after the run.
            wb = load_workbook(excel_file, read_only=True)
            try:
                summary_exists = 'Summary' in wb.sheetnames
            finally:
                wb.close()
            file_is_valid_existing = True
        except Exception as e:
            # The file exists on disk but isn't a readable Excel workbook -
            # most likely a stub (often 0 bytes) left behind by a previous run
            # that crashed or was interrupted mid-write (e.g. a killed
            # kernel), at the exact output path a later run targets again.
            # Previously this made every subsequent run for the same
            # country/hazard/period fail with a cryptic "File is not a zip
            # file" error and no recovery path other than manually finding
            # and deleting the file. Treat it as if no file existed instead.
            print(f"WARNING: Existing file '{excel_file}' could not be read as "
                  f"a valid Excel workbook ({e}) - likely left over from an "
                  f"interrupted previous run. Overwriting it with a fresh file.")

    if file_is_valid_existing:
        excel_writer = pd.ExcelWriter(excel_file, engine='openpyxl', mode='a', if_sheet_exists='replace')
    else:
        excel_writer = pd.ExcelWriter(excel_file, engine='openpyxl')

    if summary_sheet and summary_exists:
        summary_df = pd.read_excel(excel_file, sheet_name='Summary')
        dataset = merge_dfs(summary_df, dataset)

    with excel_writer:
        dataset.to_excel(excel_writer, sheet_name=sheet_name, index=False)
        

def merge_dfs(df_left, df_right, on_columns=['RP', 'Freq', 'Ex_freq'], how='outer'):

    # Get the unique columns from both DataFrames
    all_columns = list(df_left.columns.union(df_right.columns, sort=False))

    # Perform the merge
    merged_df = pd.merge(df_left, df_right, on=on_columns, how=how, suffixes=('_x', '_y'))
    common_columns = [col for col in df_left.columns if col in df_right.columns and col not in on_columns]

    # df_right (_y) holds the freshly computed values for this run; df_left (_x) is
    # whatever was already in the Summary sheet from a previous run. Prefer the new
    # value and only fall back to the stale one when the new run didn't produce it -
    # otherwise a reused output file keeps showing results from an earlier run.
    for col in common_columns:
        merged_df[col] = merged_df[f'{col}_y'].combine_first(merged_df[f'{col}_x'])
        merged_df.drop([f'{col}_x', f'{col}_y'], axis=1, inplace=True)
        
    merged_df = merged_df.groupby(on_columns, as_index=False).first()
        
    return merged_df[all_columns]


# Process exposure data
def process_exposure_data(country, haz_type, exp_cat, exp_nam, exp_year, exp_folder):

    try:
        if exp_nam is not None:
            # Use the custom exposure data if provided
            exp_ras = f"{exp_folder}/{exp_nam}.tif"
            if not os.path.exists(exp_ras):
                raise FileNotFoundError(f"Custom exposure data not found: {exp_ras}")
                 
        else:
            # Use default exposure data based on exp_cat
            if exp_cat == 'POP':
                exp_ras = f"{exp_folder}/{country}_POP.tif"
                if not os.path.exists(exp_ras):
                    print(f"Population data not found. Fetching data for {country}...")
                    input_utils.fetch_population_data(country, exp_year)
                    if not os.path.exists(exp_ras):
                        raise FileNotFoundError(f"Failed to fetch population data for {country}")
            elif exp_cat == 'BU':
                exp_ras = f"{exp_folder}/{country}_BU.tif"
                if not os.path.exists(exp_ras):
                    print(f"Built-up data not found. Fetching data for {country}...")
                    input_utils.fetch_built_up_data(country)
                    if not os.path.exists(exp_ras):
                        raise FileNotFoundError(f"Failed to fetch built-up data for {country}")
            elif exp_cat == 'AGR':
                exp_ras = f"{exp_folder}/{country}_AGR.tif"

                if not os.path.exists(exp_ras):
                    print(f"Agriculture data not found. Fetching data for {country}...")
                    input_utils.fetch_agri_data(country)
                    if not os.path.exists(exp_ras):
                        raise FileNotFoundError(f"Failed to fetch agricultural data for {country}")
            else:
                raise ValueError(f"Missing or unknown exposure category: {exp_cat}")

        if not os.path.exists(exp_ras):
            raise FileNotFoundError(f"Exposure raster not found after processing: {exp_ras}")

        # Assign a default damage factor based on the haz_type and exp_cat
        if haz_type == 'FL':
            if exp_cat == 'POP':
                damage_factor = FL_mortality_factor
            elif exp_cat == 'BU':
                damage_factor = FL_damage_factor_builtup
            elif exp_cat == 'AGR':
                damage_factor = FL_damage_factor_agri
        elif haz_type == 'TC':
            if exp_cat == 'BU':
                damage_factor = TC_damage_factor_builtup
            else:
                # No validated wind-damage curve exists for this exposure
                # category - TC_damage_factor_builtup (Eberenz et al. 2021)
                # only covers built-up stock. This was previously
                # `lambda x: x` with a single parameter, which crashed with a
                # confusing "takes 1 positional argument but 2 were given" as
                # soon as Function-type analysis called it - calc_imp_RPs
                # always calls damage_factor(haz_data, region) with 2 args,
                # regardless of hazard type or exposure category. Accepting
                # the second argument fixes the crash, but this is still only
                # a placeholder: it passes raw wind speed (m/s) through
                # unchanged as if it were a 0-1 damage fraction, which is NOT
                # a validated impact estimate for this category.
                print(f"WARNING: No wind-damage function is defined for exposure "
                      f"category '{exp_cat}' under tropical cyclones. Raw hazard "
                      f"intensity (wind speed, m/s) will be passed through "
                      f"unchanged as 'impact' - this is NOT a validated damage "
                      f"estimate (only BU/built-up has one, from Eberenz et al. "
                      f"2021). Consider 'Classes' analysis instead for a raw "
                      f"exposure-by-wind-speed breakdown of this category.")
                damage_factor = lambda x, region=None: x
        else:
                raise ValueError(f"Unknown hazard type: {haz_type}")

        return exp_ras, damage_factor

    except Exception as e:
        print(f"Error in process_exposure_data: {str(e)}")


def exception_handler(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(f"An error occurred: {e}")
            # str(e) alone (e.g. "[WinError 87] The parameter is incorrect")
            # gives no indication of WHERE the failure happened - a native/
            # GDAL-level error like that one carries no Python traceback info
            # in its message. Write the full traceback to a log file in
            # OUTPUT_DIR so it survives past the notebook's scrollback.
            try:
                log_path = os.path.join(OUTPUT_DIR, "error_log.txt")
                with open(log_path, 'a', encoding='utf-8') as log_file:
                    log_file.write(f"\n{'='*80}\n")
                    log_file.write(f"{datetime.datetime.now().isoformat()} - {func.__name__}\n")
                    log_file.write(f"args={args!r}\nkwargs={kwargs!r}\n\n")
                    log_file.write(traceback.format_exc())
                print(f"Full error details (with traceback) written to {log_path}")
            except Exception as log_error:
                print(f"WARNING: could not write detailed error log: {log_error}")
            return None

    return wrapper


# Defining the main function to run the analysis
@exception_handler
def run_analysis(
    country: str, haz_type: str, haz_cat: str, period: str, scenario: str,
    valid_RPs: list[int], min_haz_threshold: float, exp_cat: str,
    exp_nam: str, exp_year: str, adm_level: str, analysis_type: str, 
    class_edges: list[float], save_check_raster: bool, n_cores: int = None,
    use_custom_boundaries=False, custom_boundaries_file_path=None, custom_code_field=None,
    custom_name_field=None, wb_region=None, custom_boundaries_layer=None
):
    """
    Run specified analysis.

    Parameters
    ----------
    country : country ISOa3 code
    haz_type : hazard type 'FL' for floods or 'TC' for tropical cyclones
    haz_cat : hazard category
    period: time period
    scenario: SSP scenario
    valid_RPs : return period values to be considered
    min_haz_threshold : minimum value for hazard values
    exp_cat : exposure category
    exp_nam : exposure user-specified file name or source
    exp_year: exposure year of reference
    adm_level : ADM level of sub-national boundaries
    analysis_type : type of analysis (class or function)
    class_edges : class edges for class-based analysis
    save_check_raster : save intermediate results to disk?
    """

    try:
        # The probability weighting below (prob_RPs_LB/UB via -np.diff) assumes
        # valid_RPs is sorted ascending; an out-of-order list silently produces
        # negative probability bins that corrupt EAI/EAE. Sort defensively.
        valid_RPs = sorted(valid_RPs)

        # Defining the location of administrative, hazard and exposure folders
        if haz_type == 'TC':  # Strong Wind (Tropical Cyclones)
            haz_folder = f"{DATA_DIR}/HZD/GLB/STORM/{period}"
        elif haz_type == 'FL':  # Floods (FLUVIAL_UNDEFENDED, FLUVIAL_DEFENDED, etc.)
            haz_folder = f"{DATA_DIR}/HZD/{country}/{haz_cat}/{period}/{scenario.replace('-', '_')}"

        exp_folder = f"{DATA_DIR}/EXP"

        # Validating Classes analysis parameters
        if analysis_type == "Classes":
            if not class_edges:
                raise ValueError("Class edges must be provided for Classes analysis")
            is_seq = np.all(np.diff(class_edges) > 0)
            if not is_seq:
                raise ValueError("Class thresholds are not sequential. Lower classes must be less than class thresholds above.")
            bin_seq = class_edges + [np.inf]
            num_bins = len(bin_seq)
        else:
            bin_seq = None
            num_bins = None

        # Fetch the ADM data
        if use_custom_boundaries:
            print(f"Using custom boundaries from file: {custom_boundaries_file_path}")
            # A multi-layer file (e.g. GPKG) silently picks whichever layer
            # GDAL considers "default" (observed: a 1417-feature ADM4 layer
            # got loaded when the user had selected ADM level 2 in the GUI,
            # which has its own 15-feature 'FJI_ADM2' layer in the same file -
            # gpd.read_file() with no `layer=` doesn't know about adm_level at
            # all). The GUI now surfaces a layer picker for exactly this case
            # (see gui_tc_utils.py/gui_f3_utils.py's custom_boundaries_layer_
            # field) and passes its choice through as custom_boundaries_layer.
            # For callers that don't go through the GUI (or leave it
            # unselected), fall back to an unambiguous ADM-level-name match,
            # or fail loudly with the full layer list rather than silently
            # analyzing the wrong boundaries.
            selected_layer = custom_boundaries_layer
            if selected_layer is None:
                available_layers = common.list_boundary_layers(custom_boundaries_file_path)
                if len(available_layers) > 1:
                    selected_layer = common.match_adm_level_layer(available_layers, adm_level)
                    if selected_layer is None:
                        raise ValueError(
                            f"'{custom_boundaries_file_path}' contains multiple layers "
                            f"({available_layers}) and none (or more than one) "
                            f"unambiguously matches ADM level {adm_level}. Select the "
                            f"intended layer explicitly (the GUI's layer dropdown), or "
                            f"rename it to include 'ADM{adm_level}' so it can be "
                            f"identified automatically."
                        )
                    print(f"Multiple layers found in {custom_boundaries_file_path}: "
                          f"{available_layers} - using '{selected_layer}' to match "
                          f"the selected ADM level {adm_level}.")
            adm_data = gpd.read_file(custom_boundaries_file_path, layer=selected_layer)
            code_field = custom_code_field
            name_field = custom_name_field
            all_adm_codes = [code_field]
            all_adm_names = [name_field]
        else:
            print(f"Fetching ADM data for {country}, level {adm_level}")
            adm_data = input_utils.get_adm_data(country, adm_level)
            field_names = common.adm_field_mapping.get(adm_level, {})
            code_field = field_names.get('code')
            name_field = field_names.get('name')
            all_adm_codes = adm_data.columns[adm_data.columns.str.contains(r"HASC_\d$")].to_list()
            all_adm_names = adm_data.columns[adm_data.columns.str.contains(r"NAM_\d$")].to_list()

        if not (code_field and name_field):
            raise ValueError(f"Field names for ADM level {adm_level} not found")

        # Handle exposure data. This now runs BEFORE the multipart-geometry
        # fix and CRS reconciliation below it need to know the exposure
        # raster's CRS/extent - moved ahead of where it used to sit (after
        # the multipart fix) so adm_data can be reprojected to match the
        # exposure raster, and so the multipart/nested-geometry topology
        # check below runs on already-reconciled coordinates.
        print(f"Processing exposure data for {exp_cat}")
        exp_ras, damage_factor = process_exposure_data(country, haz_type, exp_cat, exp_nam, exp_year, exp_folder)

        # Importing the exposure data (original approach with chunking fallback)
        with rasterio.open(exp_ras) as src:
            original_nodata = src.nodata

        try:
            # Try original approach first (fastest)
            exp_data = rxr.open_rasterio(exp_ras)[0].astype('float32')
        except MemoryError:
            print("Memory error detected, falling back to chunked loading...")
            exp_data = rxr.open_rasterio(exp_ras, chunks=True)[0].astype('float32')
            # Compute immediately to avoid alignment issues later
            exp_data = exp_data.compute()

        # Handle nodata values
        if original_nodata is not None:
            # Mask the original nodata values
            exp_data = exp_data.where(exp_data != original_nodata)
        exp_data.rio.write_nodata(-1.0, inplace=True)
        exp_data.data[exp_data < 0.0] = 0.0

        # Administrative boundaries and the exposure raster must share a CRS
        # for zonal stats to mean anything - rasterstats reads raw vector
        # coordinates directly against the raster's own affine transform, it
        # does not reproject on your behalf. Nothing previously enforced
        # this: for the default pipeline both happened to be EPSG:4326 so it
        # silently worked, but a custom exposure raster in a different CRS
        # (e.g. EPSG:3460 for Fiji) against boundaries still in EPSG:4326
        # produced zero overlap everywhere - every exposure/impact total came
        # out 0, with no error and no warning. It also matters for
        # antimeridian-crossing countries: the exposure raster may now be
        # normalized into a local projected CRS instead of EPSG:4326 (see
        # input_utils.normalize_antimeridian_raster), and adm_data must
        # follow it there too.
        if adm_data.crs is None:
            print(f"WARNING: administrative boundaries have no CRS defined - "
                  f"assuming their coordinates already match the exposure "
                  f"raster's CRS ({exp_data.rio.crs}). If exposure/impact "
                  f"totals come out zero, check this first.")
        elif adm_data.crs != exp_data.rio.crs:
            print(f"Reprojecting administrative boundaries from {adm_data.crs} "
                  f"to match the exposure raster's CRS ({exp_data.rio.crs})...")
            adm_data = adm_data.to_crs(exp_data.rio.crs)

        # Reprojecting a large/detailed boundary set (e.g. a custom ADM4 file
        # with thousands of features) can surface pre-existing marginal
        # topology defects in the source data as outright GEOS failures -
        # observed against a real 1417-feature custom Fiji boundary file:
        # "TopologyException: side location conflict ... This can occur if
        # the input geometry is invalid", raised from has_nested_multiparts's
        # .contains() call below. make_valid() is run unconditionally (not
        # just when .is_valid is False) because GEOS predicate operations
        # like .contains() can still hit internal robustness errors on
        # geometries that report as topologically valid, particularly for
        # high-vertex-count polygons - .is_valid alone was not a reliable
        # enough signal in testing to only repair when it was False.
        invalid_count = (~adm_data.geometry.is_valid).sum()
        if invalid_count > 0:
            print(f"Note: {invalid_count} invalid geometries found in the "
                  f"administrative boundaries; repairing before topology checks.")
        adm_data['geometry'] = adm_data.geometry.make_valid()

        # Fix problematic multipart geometries for rasterstats compatibility
        # Only explode when multiparts have nested/overlapping parts within other units
        from shapely.geometry import MultiPolygon

        def has_nested_multiparts(gdf):
            """
            Check if any multipart geometry has parts that are spatially separated
            in a way that might overlap with other administrative units.
            This detects problematic cases like parts of one unit nested within another.
            """
            multipart_indices = gdf.geometry.apply(lambda geom: isinstance(geom, MultiPolygon))

            if not multipart_indices.any():
                return False

            # For each multipart geometry, check if its parts are far apart
            # (suggesting they might overlap with other units rather than just being islands)
            for idx in gdf[multipart_indices].index:
                geom = gdf.loc[idx, 'geometry']
                if isinstance(geom, MultiPolygon) and len(geom.geoms) > 1:
                    # Get bounding boxes of all parts
                    parts_bounds = [part.bounds for part in geom.geoms]

                    # Check if any parts are contained within bounding boxes of other units
                    other_units = gdf[gdf.index != idx]
                    for part in geom.geoms:
                        part_centroid = part.centroid
                        # Check if this part's centroid falls within another unit
                        for other_idx, other_geom in other_units.geometry.items():
                            if other_geom.contains(part_centroid):
                                # Found a problematic case: part of one unit inside another
                                return True

            return False

        try:
            has_multipart = has_nested_multiparts(adm_data)
        except Exception as e:
            # GEOS predicate operations (.contains() here) can still fail with
            # a TopologyException/GEOSException on complex real-world polygons
            # even after make_valid() above - observed intermittently against
            # a real 1417-feature custom boundary file. Exploding multipart
            # geometries is always a SAFE operation for rasterstats (it just
            # makes zonal stats run per-part instead of per-multipart, never
            # incorrect), so default to it rather than let an unreliable GEOS
            # predicate check abort the whole run.
            print(f"WARNING: could not reliably check for nested multipart "
                  f"geometries ({type(e).__name__}: {e}). Defaulting to "
                  f"exploding all multipart geometries, which is always safe "
                  f"for rasterstats even when not strictly necessary.")
            has_multipart = True

        if has_multipart:
            print(f"Warning: Found problematic nested multipart geometries in ADM{adm_level} boundaries.")
            print(f"Converting multipart geometries to single parts for rasterstats compatibility...")
            n_original = len(adm_data)
            # Store original index to preserve grouping information
            adm_data['_original_idx'] = adm_data.index
            adm_data = adm_data.explode(index_parts=False).reset_index(drop=True)
            n_exploded = len(adm_data)
            print(f"Converted {n_original} features to {n_exploded} single-part features")
        else:
            multipart_count = adm_data.geometry.apply(lambda geom: isinstance(geom, MultiPolygon)).sum()
            if multipart_count > 0:
                print(f"Note: Found {multipart_count} simple multipart geometries (e.g., islands) - no explosion needed.")

        # Parallel processing setup
        cores = min(len(valid_RPs), mp.cpu_count()) if n_cores is None else n_cores

        # NOTE: all_touched=False (overriding zonal_stats_partial's own
        # default of True) is deliberate here, matching the impact-side
        # calls in calc_imp_RPs below. all_touched=True is NOT partition-
        # safe: a pixel straddling the border between two adjacent admin
        # units gets counted by both units, so summing unit-level totals
        # across a country would double-count boundary pixels - worse the
        # coarser the raster is relative to unit size (e.g. STORM wind
        # rasters against small provinces). all_touched=False (centroid-in-
        # polygon) is partition-safe, at the cost of very small/thin/
        # coastal units potentially showing zero exposure if no pixel
        # center falls inside them.
        func = partial(zonal_stats_partial, raster=exp_ras, stats="sum", all_touched=False)
        geom_chunks = np.array_split(adm_data.geometry, cores)
        if cores <= 1:
            # Avoid the overhead of spawning a subprocess (Windows has no
            # fork - Pool(1) still starts a fresh interpreter via 'spawn')
            # when there's only one chunk to process anyway.
            stats_parallel = [func(chunk) for chunk in geom_chunks]
        else:
            with mp.Pool(cores) as p:
                stats_parallel = p.map(func, geom_chunks)

        exp_per_ADM = list(it.chain(*stats_parallel))

        # Creating the results pandas dataframe
        columns_to_include = all_adm_codes + all_adm_names + ["geometry"]
        # Include _original_idx if it exists (from exploded geometries)
        if '_original_idx' in adm_data.columns:
            columns_to_include.append('_original_idx')
        result_df = adm_data.loc[:, columns_to_include]
        result_df[f"ADM{adm_level}_{exp_cat}"] = [x['sum'] for x in exp_per_ADM]

        # Cleaning-up memory
        del (stats_parallel, exp_per_ADM)
        gc.collect()
        
        # Defining the list of valid prob_RPs - probability of return period
        prob_RPs = 1./np.array(valid_RPs)
        prob_RPs_LB = np.append(-np.diff(prob_RPs), prob_RPs[-1]).tolist()           # Lower bound - alternative --> prob_RPs_LB = np.append(1-prob_RPs[0],-np.diff(prob_RPs)).tolist() # Lower bound [0-1]
        prob_RPs_UB = np.insert(-np.diff(prob_RPs), 0, 0.).tolist()                  # Upper bound - alternative --> prob_RPs_UB = np.append(1-prob_RPs[0],-np.diff(prob_RPs)).tolist() # Upper bound [0-1]
        prob_RPs_Mean = ((np.array(prob_RPs_LB) + np.array(prob_RPs_UB))/2).tolist() # Mean value
        prob_RPs_df = pd.DataFrame({'RPs':valid_RPs,
                                    'prob_RPs':prob_RPs,
                                    'prob_RPs_LB':prob_RPs_LB,
                                    'prob_RPs_UB':prob_RPs_UB,
                                    'prob_RPs_Mean':prob_RPs_Mean})
        prob_RPs_df.to_csv(os.path.join(OUTPUT_DIR, f"{country}_{haz_cat}_prob_RPs.csv"), index=False)
        
        # Computing the results for each RP
        n_valid_RPs_gt_1 = len(valid_RPs) > 1
        cores = min(len(valid_RPs), mp.cpu_count()) if n_cores is None else n_cores
        params = {
            "haz_folder": haz_folder,
            "analysis_type": analysis_type,
            "country": country,
            "haz_cat": haz_cat,
            "period": period,
            "scenario": scenario,
            "exp_cat": exp_cat,
            "exp_data": exp_data,
            "min_haz_threshold": min_haz_threshold,
            "damage_factor": damage_factor,
            "save_check_raster": save_check_raster,
            "bin_seq": bin_seq,
            "num_bins": num_bins,
            "adm_data": adm_data,
        }
        # Damage functions key their regional curve differently: FL functions
        # (FL_damage_factor_builtup/agri) expect an already-resolved bucket name
        # ('AFRICA'/'ASIA'/'LAC'/'EUROPE'/'GLOBAL') from common.resolve_flood_region,
        # which also pulls EU member states out of the WB_REGION they'd otherwise
        # land in (ECA or 'Other') into their own EUROPE curve. TC_damage_factor_builtup
        # expects the country ISO3 code directly (via tc_region_mapping). Passing
        # wb_region to the TC function means it never matches a key and silently
        # falls back to the GLOBAL curve for every country.
        damage_region_arg = country if haz_type == 'TC' else common.resolve_flood_region(country, wb_region)
        func = partial(calc_imp_RPs, wb_region=damage_region_arg, **params)
        rp_chunks = np.array_split(valid_RPs, cores)
        if cores <= 1:
            # Avoid the overhead of spawning a subprocess for a single chunk.
            res = [func(chunk) for chunk in rp_chunks]
        else:
            with mp.Pool(cores) as p:
                res = p.map(func, rp_chunks)
        if not isinstance(res, list):
            to_concat = [result_df, res]
        else:
            to_concat = [result_df] + res

        result_df = pd.concat(to_concat, axis=1) # Concatenating the results
        result_df = result_df.replace(np.nan, 0) # Converting eventual nan/null to zero
        result_df = result_df_reorder_columns(result_df, valid_RPs, analysis_type, exp_cat,
                                            adm_level, all_adm_codes, all_adm_names)
        result_df = calc_EAEI(result_df, valid_RPs, prob_RPs_df, 'LB',
                            analysis_type, exp_cat, adm_level, num_bins, n_valid_RPs_gt_1)
        result_df = calc_EAEI(result_df, valid_RPs, prob_RPs_df, 'UB',
                            analysis_type, exp_cat, adm_level, num_bins, n_valid_RPs_gt_1)
        result_df = calc_EAEI(result_df, valid_RPs, prob_RPs_df, 'Mean',
                            analysis_type, exp_cat, adm_level, num_bins, n_valid_RPs_gt_1)
        result_df = result_df.round(3) # Round to three decimal places to avoid giving the impression of high precision

        # If method == 'Mean', then simplify it's name
        # If not n_valid_RPs_gt_1 and any column contains the initial part as 'RP1_', it is removed then
        replace_string = '_Mean' if n_valid_RPs_gt_1 else 'RP1'
        result_df_colnames = [s.replace(replace_string, '') for s in result_df.columns]
        result_df.columns = result_df_colnames

        # Aggregate results if multipart geometries were exploded
        if has_multipart:
            print(f"Aggregating results from exploded geometries back to original administrative units...")

            # Verify grouping column exists and has valid values
            if '_original_idx' not in result_df.columns:
                raise ValueError("Original index not found in result_df. Cannot aggregate exploded geometries.")

            # Check for NaN values in grouping columns
            grouping_col = '_original_idx'
            if result_df[grouping_col].isna().any():
                print(f"Warning: Found {result_df[grouping_col].isna().sum()} NaN values in grouping column")
                result_df = result_df.dropna(subset=[grouping_col])

            # Get numeric columns for aggregation
            numeric_cols = result_df.select_dtypes(include=[np.number]).columns.tolist()
            # Remove the grouping index from numeric columns if present
            numeric_cols = [col for col in numeric_cols if col != '_original_idx']

            # Percentage columns (e.g. "*_EAI%_*", "*_EAE%_*") are NOT additive
            # across exploded island parts - summing per-island percentages when
            # re-assembling a multi-island province (e.g. Fiji provinces like Ba
            # or Lau) inflates the province total, and worse for provinces with
            # more islands. Only the absolute columns get summed here; percentage
            # columns are recomputed below from the aggregated absolute values.
            pct_cols = [col for col in numeric_cols if '%' in col]
            sum_cols = [col for col in numeric_cols if col not in pct_cols]

            # Aggregate numeric columns by sum, keep first value for name and code fields
            agg_dict = {col: 'sum' for col in sum_cols}
            for name_col in all_adm_names + all_adm_codes:
                if name_col in result_df.columns and name_col not in numeric_cols:
                    agg_dict[name_col] = 'first'

            # Use dissolve to merge geometries back to multipart based on original index
            result_df = result_df.dissolve(by=grouping_col, aggfunc=agg_dict).reset_index(drop=True)

            # Remove the temporary grouping column
            if '_original_idx' in result_df.columns:
                result_df = result_df.drop('_original_idx', axis=1)

            # Recompute percentage columns from the now-aggregated absolute
            # values instead of trusting a sum of pre-aggregation percentages.
            adm_exp_col = f"ADM{adm_level}_{exp_cat}"
            for pct_col in pct_cols:
                abs_col = pct_col.replace('%', '')
                if abs_col in result_df.columns and adm_exp_col in result_df.columns:
                    result_df[pct_col] = safe_pct(result_df[abs_col], result_df[adm_exp_col])

            print(f"Aggregated to {len(result_df)} administrative units")

        # Write output csv table and geopackages
        save_geopackage(result_df, country, adm_level, haz_cat, exp_cat, period, scenario, analysis_type, valid_RPs,
                         source_crs=adm_data.crs)

        # The aggregation steps above (groupby/merge for island dissolve, Function/
        # Classes column cleanup) can silently demote result_df from a GeoDataFrame
        # to a plain DataFrame - the 'geometry' column of shapely objects survives,
        # but CRS tracking does not. Callers of run_analysis's return value
        # (plot_results for the map preview, saving_excel_and_gpgk_file for the
        # actual .gpkg export) both assume a properly-CRS'd GeoDataFrame; without
        # this, plot_results's own to_crs(epsg=4326) call fails outright
        # ("Cannot transform naive geometries"), and the .gpkg export can go out
        # silently mislabeled/uncorrected. Ensure what's returned here is a real,
        # EPSG:4326 GeoDataFrame regardless of what CRS adm_data ended up in
        # internally (e.g. a local Mercator CRS for an antimeridian-crossing
        # country, or a custom raster's own CRS).
        if not isinstance(result_df, gpd.GeoDataFrame):
            result_df = gpd.GeoDataFrame(result_df, geometry='geometry')
        if adm_data.crs is not None:
            result_df = result_df.set_crs(adm_data.crs, allow_override=True).to_crs(epsg=4326)
        else:
            result_df = result_df.set_crs(epsg=4326, allow_override=True)

        return result_df

    except Exception as e:
        print(f"An error occurred in run_analysis: {str(e)}")
        raise    

def calc_imp_RPs(RPs, haz_folder, analysis_type, country, haz_cat, period, scenario, exp_cat, exp_data, min_haz_threshold,
                 damage_factor, save_check_raster, bin_seq, num_bins, adm_data, wb_region):
    """
    Apply calculates for each given return period.
    """
    result_df = pd.DataFrame()
    for rp in RPs:
        if rp%1==0: rp = int(rp)
        # Loading the corresponding hazard dataset
        try:
            # We reproject using WarpedVRT as this applies the operation from disk
            # https://github.com/corteva/rioxarray/discussions/207
            # https://rasterio.readthedocs.io/en/latest/api/rasterio.vrt.html
            with rasterio.open(os.path.join(haz_folder, f"1in{rp}.tif")) as src:
                original_haz_nodata = src.nodata
                vrt_options = {
                    'src_crs': src.crs,
                    'crs': exp_data.rio.crs,
                    'transform': exp_data.rio.transform(recalc=True),
                    'height': exp_data.rio.height,
                    'width': exp_data.rio.width,
                }
                with rasterio.vrt.WarpedVRT(src, **vrt_options) as vrt:
                    try:
                        # Try original approach first (fastest)
                        haz_data = rxr.open_rasterio(vrt)[0].astype('float32')
                    except MemoryError:
                        print(f"Memory error loading hazard RP{rp}, falling back to chunked loading...")
                        haz_data = rxr.open_rasterio(vrt, chunks=True)[0].astype('float32')
                        # For chunked data, compute immediately to avoid alignment issues
                        haz_data = haz_data.compute()
                    # Mask the raster's own nodata sentinel (e.g. a large positive
                    # value or -9999) BEFORE any threshold comparison. Previously
                    # only min_haz_threshold filtered values, so a nodata sentinel
                    # above the threshold would be treated as a real, often huge,
                    # hazard intensity and contaminate the zonal-stats sums.
                    if original_haz_nodata is not None:
                        haz_data = haz_data.where(haz_data.data != original_haz_nodata)
                    haz_data.rio.write_nodata(-1.0, inplace=True)

        except rasterio._err.CPLE_OpenFailedError:
            raise IOError(f"Error occurred trying to open raster file: 1in{rp}.tif")

        # Set values below min threshold to nan (original approach)
        haz_data = haz_data.where(haz_data.data > min_haz_threshold, np.nan)

        # Capture which pixels are "affected" (i.e. exceed the user's own
        # min_haz_threshold) BEFORE haz_data is possibly overwritten with the
        # damage-factor output below. Damage functions apply their own internal
        # threshold (e.g. TC_damage_factor_builtup's Vthres=25.7 m/s), which is
        # unrelated to the user-selected min_haz_threshold slider; using
        # "damage > 0" to decide what counts as affected silently substitutes
        # that internal threshold for the user's setting.
        affected_mask = ~np.isnan(haz_data.data)

        # Checking the analysis_type
        if analysis_type == "Function":
            # Assign impact factor (this is F_i in the equations)
            haz_data = damage_factor(haz_data, wb_region)
            if save_check_raster:
                haz_data.rio.to_raster(os.path.join(OUTPUT_DIR, f"{country}_{haz_cat}_{period}_{scenario}_{rp}_{exp_cat}_haz_imp_factor.tif"))
        elif analysis_type == "Classes":
            # Assign bin values to raster data - Follows: x_{i-1} <= x_{i} < x_{i+1}
            bin_idx = np.digitize(haz_data, bin_seq).astype('int32')

        # Calculate affected exposure in ADM
        # Filter down to valid areas affected areas which have people
        affected_exp = exp_data.where(affected_mask, np.nan)

        if save_check_raster:
            affected_exp.rio.to_raster(os.path.join(OUTPUT_DIR, f"{country}_{haz_cat}_{period}_{scenario}_{rp}_{exp_cat}_affected.tif"))

        # Conduct analyses for classes
        if analysis_type == "Classes":
            del haz_data
            for bin_x in reversed(range(num_bins)):
                # Compute the impact for this class
                # all_touched=False: partition-safe (no double counting of
                # boundary pixels across adjacent units when results are
                # summed), matching the total exposure call above and the
                # Function-branch calls below.
                impact_class = gen_zonal_stats(vectors=adm_data["geometry"],
                                               raster=np.array(bin_idx == bin_x).astype('int32') * affected_exp.data,
                                               stats=["sum"], affine=affected_exp.rio.transform(), nodata=np.nan,
                                               all_touched=False)
                result_df[f"RP{rp}_{exp_cat}_C{bin_x}_exp"] = [x['sum'] for x in impact_class]
                # Compute the cumulative impact for this class
                if bin_x < (num_bins - 1):
                    result_df[f"RP{rp}_{exp_cat}_C{bin_x}_exp"] = result_df[f"RP{rp}_{exp_cat}_C{bin_x}_exp"] + \
                                                                  result_df[f"RP{rp}_{exp_cat}_C{bin_x+1}_exp"]

        # Conduct analyses for function
        if analysis_type == "Function":
            # Compute the exposure per ADM level
            # NOTE: all_touched=False below is deliberate and matches the total
            # exposure call above and the Classes branch above it. all_touched
            # controls whether a pixel merely touched by a polygon's edge
            # counts (True) or only pixels whose center falls inside (False).
            # True is NOT partition-safe: a boundary-straddling pixel gets
            # counted by every adjacent polygon it touches, so summing
            # unit-level totals (e.g. to a national total) would double-count
            # those pixels - worse the coarser the raster is relative to unit
            # size. False avoids that at the cost of very small/thin/coastal
            # units potentially showing zero exposure if no pixel center falls
            # inside them. Keeping all_touched consistent between this call and
            # the total exposure sum above is what actually matters for a given
            # unit's own EAI% to be internally consistent (numerator and
            # denominator drawn from the same pixel set) - which of the two
            # settings is used matters less than using the same one everywhere.
            affected_exp_per_ADM = gen_zonal_stats(vectors=adm_data["geometry"], raster=affected_exp.data,
                                                   stats=["sum"], affine=affected_exp.rio.transform(), nodata=np.nan,
                                                   all_touched=False)
            result_df[f"RP{rp}_{exp_cat}_exp"] = [x['sum'] for x in affected_exp_per_ADM]
            # Calculate impacted exposure in affected areas
            impact_exp = affected_exp.data * haz_data
            # If save intermediate to disk is TRUE, then
            if save_check_raster:
                impact_exp.rio.to_raster(os.path.join(OUTPUT_DIR, f"{country}_{period}_{scenario}_{rp}_{exp_cat}_impact.tif"))
            # Compute the impact per ADM level
            impact_exp_per_ADM = gen_zonal_stats(vectors=adm_data["geometry"], raster=impact_exp.data, stats=["sum"],
                                                 affine=impact_exp.rio.transform(), nodata=np.nan, all_touched=False)
            result_df[f"RP{rp}_{exp_cat}_imp"] = [x['sum'] for x in impact_exp_per_ADM]
            del (haz_data, impact_exp, impact_exp_per_ADM, affected_exp_per_ADM)

        del affected_exp
        gc.collect()

    return result_df

def result_df_reorder_columns(result_df, RPs, analysis_type, exp_cat, adm_level, all_adm_codes, all_adm_names):
    """
    Reorders the columns of result_df.
    """
    # Re-ordering and dropping selected columns for better presentation of the results

    if analysis_type != "Function":
        return result_df

    adm_column = f"ADM{adm_level}_{exp_cat}"

    all_RPs = ["RP" + str(rp) for rp in RPs]
    all_exp = [x + f"_{exp_cat}_exp" for x in all_RPs]
    all_imp = [x + f"_{exp_cat}_imp" for x in all_RPs]
    col_order = all_adm_codes + all_adm_names + [adm_column] + all_exp + all_imp + ["geometry"]

    # Preserve _original_idx if it exists (from exploded geometries)
    if '_original_idx' in result_df.columns:
        col_order.append('_original_idx')

    result_df = result_df.loc[:, col_order]

    return result_df

def safe_pct(numerator: pd.Series, denominator: pd.Series) -> pd.Series:
    """(numerator / denominator) * 100, with 0 wherever denominator is 0 (avoids inf/NaN
    for admin units with zero total exposure, e.g. uninhabited units for POP)."""
    denom = denominator.to_numpy(dtype='float64')
    num = numerator.to_numpy(dtype='float64')
    result = np.zeros_like(denom)
    valid = denom > 0
    result[valid] = (num[valid] / denom[valid]) * 100.0
    return pd.Series(result, index=numerator.index)


def calc_EAEI(result_df, RPs, prob_RPs_df, method, analysis_type, exp_cat,
              adm_level, num_bins, n_valid_RPs_gt_1):
    """
    Computes the EAE/EAI over each given return period.
    """
    for rp in RPs:

        # Exceedance Probability of return period
        freq = float(prob_RPs_df.loc[prob_RPs_df['RPs'] == rp, f'prob_RPs_{method}'].iloc[0])

        # Conduct analyses for classes
        if analysis_type == "Classes":
            # Compute the EAE for classes, if probabilistic (len(valid_RPs)>1)
            if n_valid_RPs_gt_1:
                for bin_x in reversed(range(num_bins)):
                    result_df[f"RP{rp}_{exp_cat}_C{bin_x}_EAE_tmp"] = result_df[f"RP{rp}_{exp_cat}_C{bin_x}_exp"] * freq

        # Conduct analyses for function
        if analysis_type == "Function":
            # Compute the EAI for this RP, if probabilistic (len(valid_RPs)>1)
            if n_valid_RPs_gt_1:
                result_df[f"RP{rp}_EAI_tmp"] = result_df[f"RP{rp}_{exp_cat}_imp"] * freq
        
    # Computing the EAE or EAI, if probabilistic (len(valid_RPs)>1)
    if n_valid_RPs_gt_1:
        # Computing EAE if analysis is Classes
        if analysis_type == "Classes":
            # Sum all EAI to get total EAI across all RPs and Classes
            for bin_x in reversed(range(0, num_bins)):
                C_EAE_cols = result_df.columns.str.contains(f"{exp_cat}_C{bin_x}_EAE_tmp")
                result_df.loc[:, f"{exp_cat}_C{bin_x}_EAE_{method}"] = result_df.loc[:, C_EAE_cols].sum(axis=1)

            # Calculate EAE% (Percent affected exposure per year)
            for bin_x in reversed(range(0, num_bins)):
                result_df.loc[:, f"{exp_cat}_C{bin_x}_EAE%_{method}"] = safe_pct(
                    result_df.loc[:, f"{exp_cat}_C{bin_x}_EAE_{method}"],
                    result_df.loc[:, f"ADM{adm_level}_{exp_cat}"])
        # Computing EAI if analysis is Function
        if analysis_type == "Function":
            if n_valid_RPs_gt_1:
                # Sum all EAI to get total EAI across all RPs
                result_df.loc[:, f"{exp_cat}_EAI_{method}"] = result_df.loc[:,result_df.columns.str.contains('_EAI_tmp')].sum(axis=1)
                # Calculate Exp_EAI% (Percent affected exposure per year)
                result_df.loc[:, f"{exp_cat}_EAI%_{method}"] = safe_pct(
                    result_df.loc[:, f"{exp_cat}_EAI_{method}"],
                    result_df.loc[:, f"ADM{adm_level}_{exp_cat}"])

    # Dropping selected columns for better presentation of the results
    if analysis_type == "Function":
        all_EAI = [col for col in result_df.columns if '_EAI_tmp' in col] if n_valid_RPs_gt_1 else []
        result_df = result_df.drop(all_EAI, axis=1) # dropping
    if analysis_type == "Classes":
        all_EAE = [col for col in result_df.columns if '_EAE_tmp' in col] if n_valid_RPs_gt_1 else []
        result_df = result_df.drop(all_EAE, axis=1) # dropping
        
    return result_df

def create_summary_df(result_df, valid_RPs, exp_cat):
    summary_data = []
    for rp in valid_RPs:
        row = {'RP': rp, 'Freq': 1/rp}
        
        # Check for impact column
        impact_col = next((col for col in result_df.columns if f'RP{rp}_{exp_cat}_imp' in col), None)
        if impact_col:
            row[f'{exp_cat}_impact'] = result_df[impact_col].sum()
        
        summary_data.append(row)
    
    summary_df = pd.DataFrame(summary_data)
    
    # Calculate Ex_freq
    summary_df['Ex_freq'] = summary_df['Freq'].diff().abs().shift(-1)
    summary_df.loc[summary_df.index[-1], 'Ex_freq'] = summary_df.loc[summary_df.index[-1], 'Freq']
    
    # Calculate EAI
    if f'{exp_cat}_impact' in summary_df.columns:
        summary_df[f'{exp_cat}_EAI'] = summary_df[f'{exp_cat}_impact'] * summary_df['Ex_freq']
    
    return summary_df

def save_geopackage(result_df, country, adm_level, haz_cat, exp_cat, period, scenario, analysis_type, valid_RPs,
                     source_crs=None):
    # Ensure that the geometry column is correctly recognized
    if 'geometry' not in result_df.columns and 'geom' in result_df.columns:
        result_df = result_df.rename(columns={'geom': 'geometry'})
    elif 'geometry' not in result_df.columns:
        raise ValueError("The DataFrame does not contain a geometry column.")

    # Convert to GeoDataFrame if it's not already one
    if not isinstance(result_df, gpd.GeoDataFrame):
        result_df = gpd.GeoDataFrame(result_df, geometry='geometry')

    # These geometries came from adm_data, which by this point in
    # run_analysis may have been reprojected to match the exposure raster's
    # CRS (e.g. a local Mercator CRS for an antimeridian-crossing country, or
    # a custom raster's own CRS) - it is NOT necessarily still EPSG:4326.
    # set_crs() only *labels* a CRS without transforming coordinates, so
    # blindly labelling non-4326 coordinates as EPSG:4326 here would silently
    # corrupt the output (e.g. writing local Mercator meters into a
    # geopackage/map that interprets them as WGS84 degrees). Reproject
    # (to_crs) using the CRS the geometries actually came from, so the
    # output file is genuinely in EPSG:4326 regardless of what working CRS
    # was used internally for zonal stats.
    if source_crs is not None:
        result_df = result_df.set_crs(source_crs, allow_override=True).to_crs(epsg=4326)
    else:
        # No CRS information was passed through - fall back to the previous
        # behavior (assume already EPSG:4326) rather than fail outright.
        result_df = result_df.set_crs(epsg=4326, allow_override=True)

    # Remove the geometry column for the Excel export
    df_cols = result_df.columns
    no_geom = result_df.loc[:, df_cols[~df_cols.isin(['geometry'])]].fillna(0)

    # Prepare Excel writer
    if period == '2020':
        file_prefix = f"{country}_ADM{adm_level}_{haz_cat}_{period}"
    else:
        file_prefix = f"{country}_ADM{adm_level}_{haz_cat}_{period}_{scenario}"

    # Create Excel writer object
    excel_file = os.path.join(common.OUTPUT_DIR, f"{file_prefix}.xlsx")

    if analysis_type == "Function":
        EAI_string = "EAI_" if len(valid_RPs) > 1 else ""
        sheet_name = f"{exp_cat}_{EAI_string}function"
        save_excel_file(excel_file, no_geom, sheet_name)
    elif analysis_type == "Classes":
        EAE_string = "EAE_" if len(valid_RPs) > 1 else ""
        sheet_name = f"{exp_cat}_{EAE_string}class"
        save_excel_file(excel_file, no_geom, sheet_name)
    else:
        raise ValueError("Unknown analysis type. Use 'Function' or 'Classes'.")

    return result_df  # Return the GeoDataFrame

def plot_results(result_df, exp_cat, analysis_type):
    # Convert result_df to GeoDataFrame if it's not already
    if not isinstance(result_df, gpd.GeoDataFrame):
        result_df = gpd.GeoDataFrame(result_df, geometry='geometry')
    
    # Determine the column to plot based on analysis_type
    if analysis_type == "Function":
        column = f'{exp_cat}_EAI'
    elif analysis_type == "Classes":
        column = f'RP10_{exp_cat}_C1'
    else:
        print("Unknown analysis approach")
        return None, None

    # Ensure the CRS is EPSG:4326
    result_df = result_df.to_crs(epsg=4326)

    # Filter out zero and negative values for color scaling
    non_zero_data = result_df[result_df[column] > 0]
    
    if len(non_zero_data) == 0:
        return None, None

    vmin = non_zero_data[column].min()
    vmax = non_zero_data[column].max()
    
    # Create a custom colormap
    colors = ['#FFEDA0', '#FED976', '#FEB24C', '#FD8D3C', '#FC4E2A', '#E31A1C', '#BD0026', '#800026']
    colormap = LinearColormap(colors=colors, vmin=vmin, vmax=vmax)
    
    # Create a style function that colors features based on their value
    def style_function(feature):
        value = feature['properties'][column]
        if value <= 0:
            return {
                'fillColor': 'transparent',
                'fillOpacity': 0,
                'color': 'black',
                'weight': 1,
            }
        return {
            'fillColor': colormap(value),
            'fillOpacity': 0.7,
            'color': 'black',
            'weight': 1,
        }
    
    # Create the GeoJson layer
    geojson_layer = folium.GeoJson(
        result_df,
        style_function=style_function,
        name=f"{exp_cat} - {column}"
    )
    
    return geojson_layer, colormap


def prepare_excel_gpkg_files(country, adm_level, haz_cat, period, scenario):

    file_prefix = f"{country}_ADM{adm_level}_{haz_cat}_{period}"

    if period != '2020':
        file_prefix += f"_{scenario}"

    excel_file = os.path.join(common.OUTPUT_DIR, f"{file_prefix}.xlsx")
    gpkg_file = os.path.join(common.OUTPUT_DIR, f"{file_prefix}.gpkg")

    return excel_file, gpkg_file


def prepare_sheet_name(analysis_type, return_periods, exp_cat):
    
    # Save results to Excel and GeoPackage
    if analysis_type == "Function":
        EAI_string = "EAI_" if len(return_periods) > 1 else ""
        sheet_name = f"{exp_cat}_{EAI_string}function"
    elif analysis_type == "Classes":
        EAE_string = "EAE_" if len(return_periods) > 1 else ""
        sheet_name = f"{exp_cat}_{EAE_string}class"
    else:
        raise ValueError("Unknown analysis type. Use 'Function' or 'Classes'.")    
    return sheet_name


def saving_excel_and_gpgk_file(result_df, excel_file, sheet_name, gpkg_file, exp_cat):
    # Save to Excel
    df_to_save = result_df.drop('geometry', axis=1, errors='ignore')
    save_excel_file(excel_file, df_to_save, sheet_name, summary_sheet=False)

    # Save to GeoPackage
    if isinstance(result_df, gpd.GeoDataFrame):
        result_df.to_file(gpkg_file, layer=sheet_name, driver='GPKG')
    else:
        print(f"Warning: Result for {exp_cat} is not a GeoDataFrame. Skipping GeoPackage export for this layer.")


def prepare_and_save_summary_df(summary_dfs, exp_cat_list, excel_file, return_file:bool = False):
    combined_summary = summary_dfs[0].copy().round(3)
    for df in summary_dfs[1:]:
        combined_summary = pd.merge(combined_summary, df.round(3), on=['RP', 'Freq', 'Ex_freq'], how='outer')

    # Reorder columns
    ordered_columns = ['RP', 'Freq', 'Ex_freq']
    for exp_cat in exp_cat_list:
        ordered_columns.extend([f'{exp_cat}_impact', f'{exp_cat}_EAI'])

    # Ensure all expected columns are present, fill with NaN if missing
    for col in ordered_columns:
        if col not in combined_summary.columns:
            combined_summary[col] = np.nan

    # Select only the ordered columns
    combined_summary = combined_summary[ordered_columns]

    # Save combined summary to Excel
    save_excel_file(excel_file, combined_summary, sheet_name='Summary', summary_sheet=True)
    
    if return_file:
        return combined_summary
