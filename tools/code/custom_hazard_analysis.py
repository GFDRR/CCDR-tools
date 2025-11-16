import os
import gc
import numpy as np
import pandas as pd
import geopandas as gpd
import rasterio
from rasterio.warp import Resampling, calculate_default_transform, reproject
from rasterstats import zonal_stats
from functools import partial
import multiprocess as mp
import tempfile

# Importing internal libraries
import common
import input_utils
from runAnalysis import (
    calc_EAEI, result_df_reorder_columns
)

DATA_DIR = common.DATA_DIR
OUTPUT_DIR = common.OUTPUT_DIR

# Cache for reprojected rasters to avoid redundant calculations
RASTER_CACHE = {}


def run_analysis_with_custom_hazard(
    country, haz_type, haz_cat, period, scenario, 
    return_periods, min_haz_threshold,
    exp_cat, exp_nam, exp_year, adm_level, 
    analysis_type, class_edges, 
    save_check_raster, n_cores, 
    use_custom_boundaries, custom_boundaries_file_path, 
    custom_code_field, custom_name_field, wb_region,
    # Custom hazard specific parameters
    hazard_files, custom_damage_func,
    zonal_stats_type='sum'
):
    """
    Optimized function to run analysis using custom hazard raster files.
    
    Parameters
    ----------
    country : country ISOa3 code
    haz_type : hazard type (set to 'CUSTOM' for this function)
    haz_cat : custom hazard category name
    period : time period (default '2020')
    scenario : not used for custom hazard
    return_periods : list of return periods
    min_haz_threshold : minimum value for hazard values
    exp_cat : exposure category ('POP', 'BU', or 'AGR')
    exp_nam : exposure user-specified file name or source
    exp_year : exposure year of reference
    adm_level : ADM level of sub-national boundaries
    analysis_type : type of analysis ('Function', 'Classes', or 'CustomFunction')
    class_edges : class edges for class-based analysis
    save_check_raster : save intermediate results to disk?
    n_cores : number of processing cores to use
    use_custom_boundaries : whether to use custom boundaries
    custom_boundaries_file_path : path to custom boundaries file
    custom_code_field : field name for ID in custom boundaries
    custom_name_field : field name for name in custom boundaries
    wb_region : World Bank region code
    hazard_files : dictionary mapping return periods to hazard file paths
    custom_damage_func : custom damage function to apply to hazard values
    zonal_stats_type : which statistic to use for zonal calculations ('sum', 'mean', or 'max')
    """
    try:
        # Create a custom hazard folder if needed
        custom_haz_folder = os.path.join(DATA_DIR, "HZD", "CUSTOM", haz_cat)
        os.makedirs(custom_haz_folder, exist_ok=True)

        # Define folder for exposure data
        exp_folder = f"{DATA_DIR}/EXP"

        # Clear raster cache at the beginning
        global RASTER_CACHE
        RASTER_CACHE = {}

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
            adm_data = gpd.read_file(custom_boundaries_file_path)
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

        # IMPROVEMENT #1: Load and preprocess exposure data once
        print(f"Processing exposure data for {exp_cat}")
        exp_ras, _ = process_exposure_data(country, haz_type, exp_cat, exp_nam, exp_year, exp_folder)

        # Load exposure as a numpy array with proper masking to avoid I/O operations later
        with rasterio.open(exp_ras) as src:
            exp_meta = src.meta
            exp_transform = src.transform
            exp_crs = src.crs
            exp_data_array = src.read(1)
            exp_nodata = src.nodata

            # Properly mask nodata values
            if exp_nodata is not None:
                exp_data_array = np.where(exp_data_array == exp_nodata, np.nan, exp_data_array)

            # Ensure negative values are set to 0
            exp_data_array = np.where(exp_data_array < 0, 0, exp_data_array)

        # Store the exposure metadata for reuse
        exp_metadata = {
            'transform': exp_transform,
            'crs': exp_crs,
            'shape': exp_data_array.shape,
            'nodata': exp_nodata,
            'meta': exp_meta
        }

        # Create a memory-mapped temporary file for the exposure data to share between processes
        print("Creating memory-mapped exposure data for shared access...")
        with tempfile.NamedTemporaryFile(suffix='.npy', delete=False) as tmp:
            exp_memmap_path = tmp.name

        # Save exposure array to memmap for multiprocessing
        exp_memmap = np.memmap(exp_memmap_path, dtype='float32', mode='w+', shape=exp_data_array.shape)
        exp_memmap[:] = exp_data_array[:]
        exp_memmap.flush()

        # Calculate total exposure per admin area once
        print(f"Calculating total {exp_cat} exposure using {zonal_stats_type}...")
        zones_geojson = [feature['geometry'] for feature in adm_data.__geo_interface__['features']]

        # IMPROVEMENT #7: Optimize zonal_stats parameters
        zonal_stats_params = {
            'stats': zonal_stats_type,
            'all_touched': False,  # More precise calculation
            'geojson_out': False,  # Don't need this for better performance
            'nodata': np.nan,
            'categorical': False,
            'prefix': '',
            'raster_out': False,
            'boundless': True,  # Better handling of boundary pixels
        }
        
        # Calculate total exposure (optimize with chunking for large datasets)
        if len(zones_geojson) > 100:
            # For large datasets, use parallel processing
            cores = min(mp.cpu_count(), 8)  # Limit to 8 cores max
            with mp.Pool(cores) as p:
                chunks_size = max(1, len(zones_geojson) // cores)
                zone_chunks = [zones_geojson[i:i+chunks_size] for i in range(0, len(zones_geojson), chunks_size)]
                
                func = partial(zonal_stats, raster=exp_ras, **zonal_stats_params)
                stats_results = p.map(func, zone_chunks)
                
                # Flatten results
                exp_per_ADM = [item for sublist in stats_results for item in sublist]
        else:
            # For smaller datasets, use single process
            exp_per_ADM = zonal_stats(zones_geojson, exp_ras, **zonal_stats_params)

        # Creating the results dataframe
        result_df = adm_data.loc[:, all_adm_codes + all_adm_names + ["geometry"]]
        result_df[f"ADM{adm_level}_{exp_cat}"] = [x.get(zonal_stats_type, 0) for x in exp_per_ADM]

        # Clean up
        del exp_per_ADM
        gc.collect()
        
        # Calculate probability dataframe
        prob_RPs = 1./np.array(return_periods)
        prob_RPs_LB = np.append(-np.diff(prob_RPs), prob_RPs[-1]).tolist()
        prob_RPs_UB = np.insert(-np.diff(prob_RPs), 0, 0.).tolist()
        prob_RPs_Mean = ((np.array(prob_RPs_LB) + np.array(prob_RPs_UB))/2).tolist()
        prob_RPs_df = pd.DataFrame({'RPs':return_periods,
                                    'prob_RPs':prob_RPs,
                                    'prob_RPs_LB':prob_RPs_LB,
                                    'prob_RPs_UB':prob_RPs_UB,
                                    'prob_RPs_Mean':prob_RPs_Mean})
        prob_RPs_df.to_csv(os.path.join(OUTPUT_DIR, f"{country}_{haz_cat}_prob_RPs.csv"), index=False)

        # IMPROVEMENT #1: Preprocess all hazard rasters ahead of time
        valid_rp_files = []
        for rp in return_periods:
            if rp in hazard_files and os.path.exists(hazard_files[rp]):
                valid_rp_files.append((rp, hazard_files[rp]))
            else:
                print(f"Warning: No valid hazard file found for RP {rp}")

        if not valid_rp_files:
            raise ValueError("No valid hazard files found for any return period")

        # Set up parameters for multiprocessing
        n_valid_RPs_gt_1 = len(valid_rp_files) > 1
        cores = min(len(valid_rp_files), mp.cpu_count()) if n_cores is None else n_cores
        print(f"Using {cores} cores for parallel processing")

        # Process all return periods in parallel with optimized approach
        print(f"Processing {len(valid_rp_files)} return periods...")

        # Prepare parameters dictionary for the workers
        params = {
            "analysis_type": analysis_type,
            "exp_cat": exp_cat,
            "min_haz_threshold": min_haz_threshold,
            "custom_damage_func": custom_damage_func,
            "save_check_raster": save_check_raster,
            "bin_seq": bin_seq,
            "num_bins": num_bins,
            "adm_data": adm_data,
            "country": country,
            "zonal_stats_type": zonal_stats_type,
            "wb_region": wb_region,
            "exp_memmap_path": exp_memmap_path,
            "exp_metadata": exp_metadata,
            "zones_geojson": zones_geojson
        }

        # Use multiprocessing to process each return period
        if len(valid_rp_files) > 1:
            with mp.Pool(cores) as pool:
                func = partial(process_return_period_optimized, **params)
                result_dfs = pool.map(func, valid_rp_files)

                # Filter out None results
                result_dfs = [df for df in result_dfs if df is not None]
        else:
            # Process single return period directly
            result_dfs = [process_return_period_optimized(valid_rp_files[0], **params)]

        # Clean up memory-mapped file
        safe_delete_file(exp_memmap_path)

        # Combine results
        if result_dfs and all(df is not None for df in result_dfs):
            # Concatenate the return period results
            to_concat = [result_df] + result_dfs
            result_df = pd.concat(to_concat, axis=1)
            result_df = result_df.replace(np.nan, 0)

            # Reorder columns and calculate expected annual impact/exposure
            result_df = result_df_reorder_columns(
                result_df, return_periods, analysis_type, exp_cat, 
                adm_level, all_adm_codes, all_adm_names
            )

            # Calculate EAI/EAE if multiple return periods
            if n_valid_RPs_gt_1:
                result_df = calc_EAEI(
                    result_df, return_periods, prob_RPs_df, 'LB', 
                    analysis_type, exp_cat, adm_level, num_bins, n_valid_RPs_gt_1
                )

                result_df = calc_EAEI(
                    result_df, return_periods, prob_RPs_df, 'UB', 
                    analysis_type, exp_cat, adm_level, num_bins, n_valid_RPs_gt_1
                )

                result_df = calc_EAEI(
                    result_df, return_periods, prob_RPs_df, 'Mean', 
                    analysis_type, exp_cat, adm_level, num_bins, n_valid_RPs_gt_1
                )

            # Round values for better presentation
            result_df = result_df.round(3)

            # Simplify column names if needed
            replace_string = '_Mean' if n_valid_RPs_gt_1 else 'RP1'
            result_df_colnames = [s.replace(replace_string, '') for s in result_df.columns]
            result_df.columns = result_df_colnames

            print(f"Analysis completed successfully for {len(result_dfs)} return periods")
            return result_df
        else:
            print("No valid results were produced")
            return None

    except Exception as e:
        print(f"An error occurred in custom hazard analysis: {str(e)}")
        import traceback
        traceback.print_exc()
        return None
    finally:
        # Clear raster cache
        RASTER_CACHE.clear()
        # Run garbage collection
        gc.collect()


def preprocess_hazard_raster(hazard_file, exp_metadata, memmap_dir=None):
    """
    Preprocess hazard raster to match exposure grid - returns a path to the reprojected raster

    IMPROVEMENT #1: This function reprojests hazard data once and caches it
    """
    # Check if we already processed this file
    global RASTER_CACHE
    if hazard_file in RASTER_CACHE:
        return RASTER_CACHE[hazard_file]

    # Create a temporary directory if not provided
    if memmap_dir is None:
        memmap_dir = tempfile.mkdtemp()

    output_path = os.path.join(memmap_dir, f"reprojected_{os.path.basename(hazard_file)}")

    # If already processed, return the path
    if os.path.exists(output_path):
        RASTER_CACHE[hazard_file] = output_path
        return output_path

    try:
        # Read source hazard raster
        with rasterio.open(hazard_file) as src:
            # Calculate reprojection parameters
            _, _, _ = calculate_default_transform(
                src.crs, exp_metadata['crs'],
                src.width, src.height, 
                *src.bounds,
                dst_width=exp_metadata['shape'][1],
                dst_height=exp_metadata['shape'][0]
            )

            # Update metadata for output
            output_meta = src.meta.copy()
            output_meta.update({
                'crs': exp_metadata['crs'],
                'transform': exp_metadata['transform'],
                'width': exp_metadata['shape'][1],
                'height': exp_metadata['shape'][0],
                'nodata': src.nodata
            })

            # Create output raster
            with rasterio.open(output_path, 'w', **output_meta) as dst:
                # Reproject and save
                reproject(
                    source=rasterio.band(src, 1),
                    destination=rasterio.band(dst, 1),
                    src_transform=src.transform,
                    src_crs=src.crs,
                    dst_transform=exp_metadata['transform'],
                    dst_crs=exp_metadata['crs'],
                    resampling=Resampling.bilinear
                )

        # Cache the path
        RASTER_CACHE[hazard_file] = output_path
        return output_path

    except Exception as e:
        print(f"Error preprocessing hazard raster: {str(e)}")
        raise


def process_return_period_optimized(rp_file_tuple, **kwargs):
    """
    Process a single return period with optimized approach

    IMPROVEMENT #5: Reduced I/O operations with better memory management
    """
    rp, hazard_file = rp_file_tuple

    try:
        print(f"Processing return period {rp}...")

        # Unpack required parameters
        analysis_type = kwargs.get('analysis_type')
        exp_cat = kwargs.get('exp_cat')
        min_haz_threshold = kwargs.get('min_haz_threshold', 0)
        custom_damage_func = kwargs.get('custom_damage_func')
        save_check_raster = kwargs.get('save_check_raster', False)
        bin_seq = kwargs.get('bin_seq')
        num_bins = kwargs.get('num_bins')
        adm_data = kwargs.get('adm_data')
        country = kwargs.get('country')
        zonal_stats_type = kwargs.get('zonal_stats_type', 'sum')
        wb_region = kwargs.get('wb_region')
        exp_memmap_path = kwargs.get('exp_memmap_path')
        exp_metadata = kwargs.get('exp_metadata')
        zones_geojson = kwargs.get('zones_geojson')

        # Load exposure data from memmap
        exp_shape = exp_metadata['shape']
        exp_array = np.memmap(exp_memmap_path, dtype='float32', mode='r', shape=exp_shape)

        # Create a tempdir for this process
        process_temp_dir = tempfile.mkdtemp()

        # IMPROVEMENT #1: Preprocess hazard raster to match exposure grid
        reprojected_hazard = preprocess_hazard_raster(hazard_file, exp_metadata, process_temp_dir)

        # Load hazard data once
        with rasterio.open(reprojected_hazard) as src:
            haz_array = src.read(1)
            _ = src.transform
            haz_nodata = src.nodata

            # Apply threshold to hazard data
            if haz_nodata is not None:
                haz_array = np.where(haz_array == haz_nodata, np.nan, haz_array)

            # Apply minimum threshold
            haz_array = np.where(haz_array <= min_haz_threshold, np.nan, haz_array)

        # Create result dataframe
        result_df = pd.DataFrame(index=adm_data.index)

        # Identify affected exposure (where hazard > 0 and not nan)
        valid_mask = ~np.isnan(haz_array)
        affected_exp = np.copy(exp_array)
        affected_exp[~valid_mask] = np.nan

        # Save affected exposure if requested
        if save_check_raster:
            affected_exp_path = os.path.join(process_temp_dir, f"affected_exp_rp{rp}.tif")
            with rasterio.open(
                affected_exp_path, 'w', driver='GTiff', height=exp_shape[0], width=exp_shape[1],
                count=1, dtype='float32', crs=exp_metadata['crs'], 
                transform=exp_metadata['transform'], nodata=np.nan
            ) as dst:
                dst.write(affected_exp, 1)

        # Process differently based on analysis approach
        if analysis_type == "Classes":
            # For classes approach
            # Create a classified array
            bin_idx = np.zeros_like(haz_array)
            for i, threshold in enumerate(bin_seq):
                # Digitize into bins
                if i < len(bin_seq) - 1:
                    bin_mask = (haz_array >= threshold) & (haz_array < bin_seq[i+1]) & valid_mask
                else:
                    bin_mask = (haz_array >= threshold) & valid_mask
                bin_idx[bin_mask] = i

            # For each class, calculate exposure
            for bin_x in reversed(range(num_bins)):
                # Create a mask for this class
                class_mask = (bin_idx == bin_x)

                # Apply the mask to the affected exposure
                class_exp = np.copy(affected_exp)
                class_exp[~class_mask] = np.nan

                # Calculate zonal statistics for this class
                class_path = os.path.join(process_temp_dir, f"class_{bin_x}.tif")
                with rasterio.open(
                    class_path, 'w', driver='GTiff', height=exp_shape[0], width=exp_shape[1],
                    count=1, dtype='float32', crs=exp_metadata['crs'],
                    transform=exp_metadata['transform'], nodata=np.nan
                ) as dst:
                    dst.write(class_exp, 1)

                # IMPROVEMENT #7: Optimized zonal_stats
                zonal_result = zonal_stats(
                    zones_geojson, 
                    class_path,
                    stats=zonal_stats_type,
                    all_touched=False,
                    geojson_out=False,
                    nodata=np.nan,
                    categorical=False,
                    boundary_only=False,
                    boundless=True
                )

                # Add the results to the dataframe
                result_df[f"RP{rp}_{exp_cat}_C{bin_x}_exp"] = [x.get(zonal_stats_type, 0) for x in zonal_result]

                # Delete temporary class file
                os.remove(class_path)

            # Calculate cumulative exposure for classes
            for bin_x in reversed(range(num_bins-1)):
                result_df[f"RP{rp}_{exp_cat}_C{bin_x}_exp"] = (
                    result_df[f"RP{rp}_{exp_cat}_C{bin_x}_exp"] + 
                    result_df[f"RP{rp}_{exp_cat}_C{bin_x+1}_exp"]
                )

        else:  # Function approach
            # Calculate affected exposure per admin area
            affected_path = os.path.join(process_temp_dir, f"affected_exp_rp{rp}_total.tif")
            with rasterio.open(
                affected_path, 'w', driver='GTiff', height=exp_shape[0], width=exp_shape[1],
                count=1, dtype='float32', crs=exp_metadata['crs'], transform=exp_metadata['transform'],
                nodata=np.nan
            ) as dst:
                dst.write(affected_exp, 1)

            affected_stats = zonal_stats(
                zones_geojson,
                affected_path,
                stats=zonal_stats_type,
                all_touched=False,
                nodata=np.nan,
                boundless=True
            )

            result_df[f"RP{rp}_{exp_cat}_exp"] = [x.get(zonal_stats_type, 0) for x in affected_stats]

            # IMPROVEMENT #2: Vectorized damage function application
            try:
                # Create a copy of hazard array for damage calculation
                damage_values = np.zeros_like(haz_array)

                # Apply the damage function only to valid pixels
                # This is a fully vectorized operation that applies custom_damage_func to all elements at once
                if valid_mask.any():
                    # Apply custom damage function to get damage factors
                    # wb_region is passed as a scalar to all elements
                    damage_values[valid_mask] = custom_damage_func(haz_array[valid_mask], wb_region)

                    # Ensure damage values are between 0 and 1
                    damage_values = np.clip(damage_values, 0, 1)

                # Calculate impact (exposure * damage factor)
                impact_values = affected_exp * damage_values

                # Save impact raster if requested
                if save_check_raster:
                    impact_path = os.path.join(OUTPUT_DIR, f"{country}_CUSTOM_{rp}_{exp_cat}_impact.tif")
                    with rasterio.open(
                        impact_path, 'w', driver='GTiff', height=exp_shape[0], width=exp_shape[1],
                        count=1, dtype='float32', crs=exp_metadata['crs'], transform=exp_metadata['transform'],
                        nodata=np.nan
                    ) as dst:
                        dst.write(impact_values, 1)

                # Write impact to temporary file for zonal stats
                impact_path = os.path.join(process_temp_dir, f"impact_rp{rp}.tif")
                with rasterio.open(
                    impact_path, 'w', driver='GTiff', height=exp_shape[0], width=exp_shape[1],
                    count=1, dtype='float32', crs=exp_metadata['crs'], transform=exp_metadata['transform'],
                    nodata=np.nan
                ) as dst:
                    dst.write(impact_values, 1)

                # Calculate zonal statistics for impact
                impact_stats = zonal_stats(
                    zones_geojson,
                    impact_path,
                    stats=zonal_stats_type,
                    all_touched=False,
                    nodata=np.nan,
                    boundless=True
                )

                result_df[f"RP{rp}_{exp_cat}_imp"] = [x.get(zonal_stats_type, 0) for x in impact_stats]

                # Delete temporary impact file
                os.remove(impact_path)

            except Exception as e:
                print(f"Error applying damage function for RP {rp}: {str(e)}")
                # Add empty columns as fallback
                result_df[f"RP{rp}_{exp_cat}_imp"] = [0] * len(adm_data)

        # Clean up tempdir after processing
        try:
            for file in os.listdir(process_temp_dir):
                try:
                    os.remove(os.path.join(process_temp_dir, file))
                except:
                    pass
            os.rmdir(process_temp_dir)
        except:
            pass

        return result_df

    except Exception as e:
        print(f"Error processing return period {rp}: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


def process_exposure_data(country, haz_type, exp_cat, exp_nam, exp_year, exp_folder):
    """Process exposure data - adapted from runAnalysis.py"""
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

        # For custom hazard we use the provided damage function
        damage_factor = lambda x: x  # This is not used for custom hazard analysis

        return exp_ras, damage_factor

    except Exception as e:
        print(f"Error in process_exposure_data: {str(e)}")
        raise


# Add this function to custom_hazard_analysis.py
def safe_delete_file(file_path):
    """
    Safely delete a file, handling locked files gracefully.

    Args:
        file_path (str): Path to the file to delete
    """
    import os
    import gc
    import time

    # Run garbage collection to release any lingering references
    gc.collect()

    # Try to delete the file, with a few retries
    max_attempts = 3
    for attempt in range(max_attempts):
        try:
            if os.path.exists(file_path):
                os.unlink(file_path)
            return  # Successfully deleted or file doesn't exist
        except (PermissionError, OSError) as e:
            if attempt < max_attempts - 1:
                # Wait a bit before retrying
                time.sleep(0.5)
                gc.collect()  # Force another garbage collection
            else:
                # On last attempt, just warn instead of failing
                print(f"Warning: Could not delete temporary file {file_path}: {str(e)}")
                print("This is not critical, but you may want to clean up temporary files manually later.")
