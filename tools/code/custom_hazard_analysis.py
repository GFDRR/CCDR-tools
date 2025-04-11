import os
import gc
import warnings
import numpy as np
import pandas as pd
import geopandas as gpd
import folium
from branca.colormap import LinearColormap
import rasterio
import rioxarray as rxr
from rasterstats import gen_zonal_stats, zonal_stats

# Importing internal libraries
import common
import input_utils
from runAnalysis import (
    calc_EAEI, result_df_reorder_columns, merge_dfs, zonal_stats_partial,
    chunks, zonal_stats_parallel
)

# Importing the libraries for parallel processing
import itertools as it
from functools import partial
import multiprocess as mp

DATA_DIR = common.DATA_DIR
OUTPUT_DIR = common.OUTPUT_DIR

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
    zonal_stats_type='sum'  # Add this new parameter with 'sum' as default
):
    """
    Run analysis using custom hazard raster files.
    
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

        # Handle exposure data
        print(f"Processing exposure data for {exp_cat}")
        exp_ras, _ = process_exposure_data(country, haz_type, exp_cat, exp_nam, exp_year, exp_folder)

        # Importing the exposure data
        # Open the raster dataset
        with rasterio.open(exp_ras) as src:
            original_nodata = src.nodata
        exp_data = rxr.open_rasterio(exp_ras)[0]  # Open exposure dataset
        # Handle nodata values
        if original_nodata is not None:
            # Mask the original nodata values
            exp_data = exp_data.where(exp_data != original_nodata)
        exp_data.rio.write_nodata(-1.0, inplace=True)
        exp_data.data[exp_data < 0.0] = 0.0

        # Parallel processing setup
        cores = min(len(return_periods), mp.cpu_count()) if n_cores is None else n_cores

        with mp.Pool(cores) as p:
            # Get total exposure for each ADM area using the specified zonal stats type
            func = partial(zonal_stats_partial, raster=exp_ras, stats=zonal_stats_type)
            stats_parallel = p.map(func, np.array_split(adm_data.geometry, cores))

        exp_per_ADM = list(it.chain(*stats_parallel))

        # Creating the results pandas dataframe
        result_df = adm_data.loc[:, all_adm_codes + all_adm_names + ["geometry"]]
        result_df[f"ADM{adm_level}_{exp_cat}"] = [x[zonal_stats_type] for x in exp_per_ADM]

        # Cleaning-up memory
        del (stats_parallel, exp_per_ADM)
        gc.collect()
        
        # Defining the list of valid prob_RPs - probability of return period
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
        
        # Computing the results for each RP
        n_valid_RPs_gt_1 = len(return_periods) > 1
        cores = min(len(return_periods), mp.cpu_count()) if n_cores is None else n_cores
        
        # Process each return period
        result_dfs = []
        for rp in return_periods:
            if rp%1==0: 
                rp = int(rp)
                
            print(f"Processing return period {rp}...")
            
            # Get the hazard file for this return period
            hazard_file = hazard_files.get(rp)
            if not hazard_file or not os.path.exists(hazard_file):
                print(f"Warning: No hazard file found for return period {rp}")
                continue
                
            # Process the hazard raster
            try:
                df = process_return_period(
                    rp, hazard_file, analysis_type, exp_cat, exp_data, 
                    min_haz_threshold, custom_damage_func, wb_region,
                    save_check_raster, bin_seq, num_bins, adm_data, country,
                    zonal_stats_type  # Pass the zonal_stats_type to the function
                )
                result_dfs.append(df)
            except Exception as e:
                print(f"Error processing return period {rp}: {str(e)}")
                import traceback
                traceback.print_exc()
        
        # Combine all return period results
        if result_dfs:
            # Concatenate the return period results
            to_concat = [result_df] + result_dfs
            result_df = pd.concat(to_concat, axis=1)
            result_df = result_df.replace(np.nan, 0)  # Converting eventual nan/null to zero
            
            # Reorder columns and calculate expected annual impact/exposure
            result_df = result_df_reorder_columns(
                result_df, return_periods, analysis_type, exp_cat, 
                adm_level, all_adm_codes, all_adm_names
            )
            
            if n_valid_RPs_gt_1:
                # Calculate EAI/EAE using different methods
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
            
            result_df = result_df.round(3)  # Round to three decimal places
            
            # If method == 'Mean', then simplify it's name
            # If not n_valid_RPs_gt_1 and any column contains the initial part as 'RP1_', it is removed then
            replace_string = '_Mean' if n_valid_RPs_gt_1 else 'RP1'
            result_df_colnames = [s.replace(replace_string, '') for s in result_df.columns]
            result_df.columns = result_df_colnames
            
            return result_df
        else:
            print("No valid hazard data was processed")
            return None

    except Exception as e:
        print(f"An error occurred in custom hazard analysis: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def process_return_period(
    rp, hazard_file, analysis_type, exp_cat, exp_data, 
    min_haz_threshold, damage_factor, wb_region,
    save_check_raster, bin_seq, num_bins, adm_data, country,
    zonal_stats_type='sum'  # Add this new parameter with 'sum' as default
):
    """Process a single return period hazard file"""
    result_df = pd.DataFrame()
    
    # Loading the corresponding hazard dataset
    try:
        # We reproject using WarpedVRT as this applies the operation from disk
        with rasterio.open(hazard_file) as src:
            vrt_options = {
                'src_crs': src.crs,
                'crs': exp_data.rio.crs,
                'transform': exp_data.rio.transform(recalc=True),
                'height': exp_data.rio.height,
                'width': exp_data.rio.width,
            }
            with rasterio.vrt.WarpedVRT(src, **vrt_options) as vrt:
                haz_data = rxr.open_rasterio(vrt)[0]
                haz_data.rio.write_nodata(-1.0, inplace=True)

    except Exception as e:
        raise IOError(f"Error occurred opening hazard file: {str(e)}")

    # Set values below min threshold to nan
    haz_data = haz_data.where(haz_data.data > min_haz_threshold, np.nan)
    
    # Checking the analysis_type
    if analysis_type == "Function" or analysis_type == "CustomFunction":
        # Assign impact factor (this is F_i in the equations)
        haz_data = damage_factor(haz_data, wb_region)
        if save_check_raster:
            output_path = os.path.join(OUTPUT_DIR, f"{country}_CUSTOM_{rp}_{exp_cat}_haz_imp_factor.tif")
            haz_data.rio.to_raster(output_path)
    elif analysis_type == "Classes":
        # Assign bin values to raster data
        bin_idx = np.digitize(haz_data, bin_seq)

    # Calculate affected exposure in ADM
    # Filter down to valid areas affected areas which have people
    affected_exp = exp_data.where(haz_data.data > 0, np.nan)

    if save_check_raster:
        output_path = os.path.join(OUTPUT_DIR, f"{country}_CUSTOM_{rp}_{exp_cat}_affected.tif")
        affected_exp.rio.to_raster(output_path)
    
    # Conduct analyses for classes
    if analysis_type == "Classes":
        del haz_data
        for bin_x in reversed(range(num_bins)):
            # Compute the impact for this class using the specified zonal stats type
            impact_class = gen_zonal_stats(vectors=adm_data["geometry"],
                                          raster=np.array(bin_idx == bin_x).astype(int) * affected_exp.data,
                                          stats=[zonal_stats_type], affine=affected_exp.rio.transform(), nodata=np.nan)
            result_df[f"RP{rp}_{exp_cat}_C{bin_x}_exp"] = [x[zonal_stats_type] for x in impact_class]
            # Compute the cumulative impact for this class
            if bin_x < (num_bins - 1):
                result_df[f"RP{rp}_{exp_cat}_C{bin_x}_exp"] = result_df[f"RP{rp}_{exp_cat}_C{bin_x}_exp"] + \
                                                             result_df[f"RP{rp}_{exp_cat}_C{bin_x+1}_exp"]

    # Conduct analyses for function
    if analysis_type == "Function" or analysis_type == "CustomFunction":
        # Compute the exposure per ADM level using the specified zonal stats type
        affected_exp_per_ADM = gen_zonal_stats(vectors=adm_data["geometry"], raster=affected_exp.data,
                                              stats=[zonal_stats_type], affine=affected_exp.rio.transform(), nodata=np.nan)
        result_df[f"RP{rp}_{exp_cat}_exp"] = [x[zonal_stats_type] for x in affected_exp_per_ADM]
        
        # Calculate impacted exposure in affected areas
        impact_exp = affected_exp.data * haz_data
        
        # If save intermediate to disk is TRUE, then
        if save_check_raster:
            output_path = os.path.join(OUTPUT_DIR, f"{country}_CUSTOM_{rp}_{exp_cat}_impact.tif")
            impact_exp.rio.to_raster(output_path)
            
        # Compute the impact per ADM level using the specified zonal stats type
        impact_exp_per_ADM = gen_zonal_stats(vectors=adm_data["geometry"], raster=impact_exp.data, 
                                            stats=[zonal_stats_type], affine=impact_exp.rio.transform(), nodata=np.nan)
        result_df[f"RP{rp}_{exp_cat}_imp"] = [x[zonal_stats_type] for x in impact_exp_per_ADM]
        del (haz_data, impact_exp, impact_exp_per_ADM, affected_exp_per_ADM)

    del affected_exp
    gc.collect()

    return result_df

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