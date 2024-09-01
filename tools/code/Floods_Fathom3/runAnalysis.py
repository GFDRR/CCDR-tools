# Required libraries
import os, gc
import numpy as np
import pandas as pd
import geopandas as gpd

import rasterio
import rioxarray as rxr
from rasterstats import gen_zonal_stats, zonal_stats

import requests
from shapely.geometry import shape

# Importing the required packages
import common
from damageFunctions import mortality_factor, damage_factor_builtup, damage_factor_agri

# Importing the libraries for parallel processing
import itertools as it
from functools import partial
import multiprocess as mp


DATA_DIR = common.DATA_DIR
OUTPUT_DIR = common.OUTPUT_DIR





# Defining functions for parallel processing of zonal_stats
def chunks(iterable_data, n):
    it_data = it.iter(iterable_data)
    for chunk in it.iter(lambda: list(it.islice(it_data, n)), []):
        yield chunk



def zonal_stats_partial(feats, raster, stats="*", affine=None, nodata=None, all_touched=True):
    # Partial zonal stats for a parallel processing a list of features
    return zonal_stats(feats, raster, stats=stats, affine=affine, nodata=nodata, all_touched=all_touched)

def zonal_stats_parallel(args):
    # Zonal stats for a parallel processing a list of features
    return zonal_stats_partial(*args)

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
def fetch_population_data(country: str, exp_year: str):
    dataset_path = f"Global_2000_2020_Constrained/{exp_year}/BSGM/{country}/{country.lower()}_ppp_{exp_year}_UNadj_constrained.tif"
    download_url = f"{common.worldpop_url}{dataset_path}"

    try:
        response = requests.get(download_url)
        
        if response.status_code != 200:
            print(f"Failed to fetch data. Status code: {response.status_code}")
            print(f"Response text: {response.text}")

        file_name = f"{DATA_DIR}/EXP/{country}_POP{exp_year}.tif"
        with open(file_name, 'wb') as file:
            file.write(response.content)
        print(f"Data downloaded successfully and saved as {file_name}")

    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")

# Defining the main function to run the analysis
def run_analysis(country: str, haz_cat: str, period: str, scenario: str, valid_RPs: list[int],
                 min_haz_threshold: float, exp_cat: str, exp_nam: str, exp_year: str, adm_level: str,
                 analysis_type: str, class_edges: list[float], 
                 save_check_raster: bool, n_cores: int = None):
    """
    Run specified analysis.

    Parameters
    ----------
    country : country ISOa3 code
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
    print("Running analysis...")
    
    # Running the initial checks =======================================================================================
 
    # Defining the location of administrative, hazard and exposure folders
    haz_folder = f"{DATA_DIR}/HZD/{country}/{haz_cat}/{period}/{scenario}"  # Hazard folder
    exp_folder = f"{DATA_DIR}/EXP"  # Exposure folder

    # If the analysis type is "Classes", then make sure that the user-defined classes are valid
    bin_seq = None
    num_bins = None
    if analysis_type == "Classes":
        # Ensure class threshold values are valid
        is_seq = np.all(np.diff(class_edges) > 0)
        if not is_seq:
            ValueError(
                "Class thresholds are not sequential. Lower classes must be less than class thresholds above.")
            exit()
        bin_seq = class_edges + [np.inf]
        num_bins = len(bin_seq)

    # Fetch the ADM data based on country code and adm_level values
    adm_data = get_adm_data(country, adm_level)

    if adm_data is not None:
        # Get the correct field names based on the administrative level
        field_names = common.adm_field_mapping.get(adm_level, {})
        code_field = field_names.get('code')
        name_field = field_names.get('name')
        wb_region = adm_data['WB_REGION'].iloc[0]

        if code_field and name_field:
            # Extract the relevant columns
            all_adm_codes = adm_data.columns.str.contains(r"HASC_\d$")
            all_adm_names = adm_data.columns.str.contains(r"NAM_\d$")
            all_adm_codes = adm_data.columns[all_adm_codes].to_list()
            all_adm_names = adm_data.columns[all_adm_names].to_list()
        else:
            print(f"Field names for ADM level {adm_level} not found.")
    else:
        raise ValueError("ADM data not available or WB_REGION attribute not found!")

    # Checking which kind of exposed category is being considered...
    print("Looking for exposure data...")

    # If the exposed category is population
    if exp_cat == 'POP' and exp_nam is None:
        fetch_population_data(country, exp_year)
        damage_factor = mortality_factor
        exp_ras = f"{exp_folder}/{country}_POP{exp_year}.tif"

    # If the exposed category is built-up area
    elif exp_cat == 'BU' and exp_nam is None:
        damage_factor = damage_factor_builtup
        exp_ras = f"{exp_folder}/{country}_BU.tif"

    # If the exposed category is agriculture
    elif exp_cat == 'AGR' and exp_nam is None:
        damage_factor = lambda x: damage_factor_agri(x, wb_region)
        exp_ras = f"{exp_folder}/{country}_AGR.tif"

    # If user-specified exposure file name is passed. Please specify appropriate damage factor to use from DamageFunctions.py
    elif exp_nam is not None:
        exp_ras = f"{exp_folder}/{exp_nam}.tif"
        damage_factor = mortality_factor
        exp_cat = str(exp_nam)

    # If the exposed category is missing, then give an error
    else:
        exp_ras = None
        raise ValueError(f"Missing or unknown data layer {exp_cat}")

    # Running the analysis
    # Importing the exposure data
    exp_data = rxr.open_rasterio(exp_ras)[0]  # Open exposure dataset
    exp_data.rio.write_nodata(-1.0, inplace=True)
    exp_data.data[exp_data < 0.0] = 0.0

    # Parallel processing setup
    cores = min(len(valid_RPs), mp.cpu_count()) if n_cores is None else n_cores

    with mp.Pool(cores) as p:
        # Get total exposure for each ADM area
        func = partial(zonal_stats_partial, raster=exp_ras, stats="sum")
        stats_parallel = p.map(func, np.array_split(adm_data.geometry, cores))

    exp_per_ADM = list(it.chain(*stats_parallel))

    # Creating the results pandas dataframe
    result_df = adm_data.loc[:, all_adm_codes + all_adm_names + ["geometry"]]
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
    prob_RPs_df.to_csv(os.path.join(common.OUTPUT_DIR, f"{country}_{haz_cat}_prob_RPs.csv"), index=False)
    
    # Computing the results for each RP
    n_valid_RPs_gt_1 = len(valid_RPs) > 1
    cores = min(len(valid_RPs), mp.cpu_count()) if n_cores is None else n_cores
    with mp.Pool(cores) as p:
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
        func = partial(calc_imp_RPs, wb_region=wb_region, **params)
        res = p.map(func, np.array_split(valid_RPs, cores))
    if not isinstance(res, list):
        to_concat = [result_df, res]
    else:
        to_concat = [result_df] + res

    result_df = pd.concat(to_concat, axis=1) # Concatenating the results
    result_df = result_df.replace(np.nan, 0) # Converting eventual nan/null to zero
    result_df = result_df_reorder_columns(result_df, valid_RPs, analysis_type, exp_cat, 
                                          adm_level, all_adm_codes, all_adm_names)
    result_df = calc_EAEI(result_df, valid_RPs, prob_RPs_df, 'LB', 
                          analysis_type, country, haz_cat, period, scenario, exp_cat, 
                          adm_level, save_check_raster, num_bins, n_valid_RPs_gt_1)
    result_df = calc_EAEI(result_df, valid_RPs, prob_RPs_df, 'UB', 
                          analysis_type, country, haz_cat, period, scenario, exp_cat, 
                          adm_level, save_check_raster, num_bins, n_valid_RPs_gt_1)
    result_df = calc_EAEI(result_df, valid_RPs, prob_RPs_df, 'Mean', 
                          analysis_type, country, haz_cat, period, scenario, exp_cat, 
                          adm_level, save_check_raster, num_bins, n_valid_RPs_gt_1)
    result_df = result_df.round(3) # Round to three decimal places to avoid giving the impression of high precision
    
    # If method == 'Mean', then simplify it's name    
    # If not n_valid_RPs_gt_1 and any column contains the initial part as 'RP1_', it is removed then
    replace_string = '_Mean' if n_valid_RPs_gt_1 else 'RP1'
    result_df_colnames = [s.replace(replace_string, '') for s in result_df.columns]
    result_df.set_axis(result_df_colnames, axis=1, inplace=True)
    
    # Write output csv table
    df_cols = result_df.columns
    no_geom = result_df.loc[:, df_cols[~df_cols.isin(['geometry'])]].fillna(0)
    file_prefix = f"{country}_ADM{adm_level}_{haz_cat}_{exp_cat}_{exp_year}"
    if analysis_type == "Function":
        EAI_string = "EAI_" if len(valid_RPs) > 1 else ""
        no_geom.to_csv(os.path.join(common.OUTPUT_DIR, f"{file_prefix}_{EAI_string}function.csv"), index=False)
        result_df.to_file(os.path.join(common.OUTPUT_DIR, f"{file_prefix}_{EAI_string}function.gpkg"))
    elif analysis_type == "Classes":
        EAE_string = "EAE_" if len(valid_RPs) > 1 else ""
        no_geom.to_csv(os.path.join(common.OUTPUT_DIR, f"{file_prefix}_{EAE_string}class.csv"), index=False)
        result_df.to_file(os.path.join(common.OUTPUT_DIR, f"{file_prefix}_{EAE_string}class.gpkg"))

    # Cleaning-up memory
    del (country, haz_cat, valid_RPs, min_haz_threshold, exp_cat, adm_level)
    del (analysis_type, class_edges, save_check_raster)
    del (haz_folder, exp_folder)
    del (exp_ras, exp_data)
    del (adm_data, all_adm_codes, all_adm_names)
    del (result_df)

    # Finishing the analysis
    print("Finished analysis.")


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

        except rasterio._err.CPLE_OpenFailedError:
            raise IOError(f"Error occurred trying to open raster file: 1in{rp}.tif")

        # Set values below min threshold to nan
        haz_data = haz_data.where(haz_data.data > min_haz_threshold, np.nan)
        
        # Checking the analysis_type
        if analysis_type == "Function":
            # Assign impact factor (this is F_i in the equations)
            haz_data = damage_factor(haz_data, wb_region)
            if save_check_raster:
                haz_data.rio.to_raster(os.path.join(common.OUTPUT_DIR, f"{country}_{haz_cat}_{period}_{scenario}_{rp}_{exp_cat}_haz_imp_factor.tif"))
        elif analysis_type == "Classes":
            # Assign bin values to raster data - Follows: x_{i-1} <= x_{i} < x_{i+1}
            bin_idx = np.digitize(haz_data, bin_seq)

        # Calculate affected exposure in ADM
        # Filter down to valid areas affected areas which have people
        affected_exp = exp_data.where(haz_data.data > 0, np.nan)

        if save_check_raster:
            affected_exp.rio.to_raster(os.path.join(common.OUTPUT_DIR, f"{country}_{haz_cat}_{period}_{scenario}_{rp}_{exp_cat}_affected.tif"))
        
        # Conduct analyses for classes
        if analysis_type == "Classes":
            del haz_data
            for bin_x in reversed(range(num_bins)):
                # Compute the impact for this class
                impact_class = gen_zonal_stats(vectors=adm_data["geometry"],
                                               raster=np.array(bin_idx == bin_x).astype(int) * affected_exp.data,
                                               stats=["sum"], affine=affected_exp.rio.transform(), nodata=np.nan)
                result_df[f"RP{rp}_{exp_cat}_C{bin_x}_exp"] = [x['sum'] for x in impact_class]
                # Compute the cumulative impact for this class
                if bin_x < (num_bins - 1):
                    result_df[f"RP{rp}_{exp_cat}_C{bin_x}_exp"] = result_df[f"RP{rp}_{exp_cat}_C{bin_x}_exp"] + \
                                                                  result_df[f"RP{rp}_{exp_cat}_C{bin_x+1}_exp"]

        # Conduct analyses for function
        if analysis_type == "Function":
            # Compute the exposure per ADM level
            affected_exp_per_ADM = gen_zonal_stats(vectors=adm_data["geometry"], raster=affected_exp.data,
                                                   stats=["sum"], affine=affected_exp.rio.transform(), nodata=np.nan)
            result_df[f"RP{rp}_{exp_cat}_exp"] = [x['sum'] for x in affected_exp_per_ADM]
            # Calculate impacted exposure in affected areas
            impact_exp = affected_exp.data * haz_data
            # If save intermediate to disk is TRUE, then
            if save_check_raster:
                impact_exp.rio.to_raster(os.path.join(common.OUTPUT_DIR, f"{country}_{period}_{scenario}_{rp}_{exp_cat}_impact.tif"))
            # Compute the impact per ADM level
            impact_exp_per_ADM = gen_zonal_stats(vectors=adm_data["geometry"], raster=impact_exp.data, stats=["sum"],
                                                 affine=impact_exp.rio.transform(), nodata=np.nan)
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
    if analysis_type == "Function":
        all_RPs = ["RP" + str(rp) for rp in RPs]
        all_exp = [x + f"_{exp_cat}_exp" for x in all_RPs]
        all_imp = [x + f"_{exp_cat}_imp" for x in all_RPs]
        col_order = all_adm_codes + all_adm_names + [f"ADM{adm_level}_{exp_cat}"] + all_exp + all_imp + ["geometry"]
        result_df = result_df.loc[:, col_order]

    return result_df

def calc_EAEI(result_df, RPs, prob_RPs_df, method, analysis_type, country, haz_cat, period, scenario, exp_cat, 
              adm_level, save_check_raster, num_bins, n_valid_RPs_gt_1):
    """
    Computes the EAE/EAI over each given return period.
    """
    for rp in RPs:

        # Probability of return period
        freq = float(prob_RPs_df['prob_RPs_'+method].loc[prob_RPs_df['RPs'] == rp])

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
                if save_check_raster:
                    EAI_i = impact_exp * freq
                    EAI_i.rio.to_raster(os.path.join(common.OUTPUT_DIR, f"{country}_{haz_cat}_{period}_{scenario}_{rp}_{exp_cat}_EAI.tif"))
        
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
                result_df.loc[:, f"{exp_cat}_C{bin_x}_EAE%_{method}"] = (result_df.loc[:,f"{exp_cat}_C{bin_x}_EAE_{method}"] / 
                                                                         result_df.loc[:,f"ADM{adm_level}_{exp_cat}"]) * 100.0
        # Computing EAI if analysis is Function
        if analysis_type == "Function":
            if n_valid_RPs_gt_1:
                # Sum all EAI to get total EAI across all RPs
                result_df.loc[:, f"{exp_cat}_EAI_{method}"] = result_df.loc[:,result_df.columns.str.contains('_EAI_tmp')].sum(axis=1)
                # Calculate Exp_EAI% (Percent affected exposure per year)
                result_df.loc[:, f"{exp_cat}_EAI%_{method}"] = (result_df.loc[:, f"{exp_cat}_EAI_{method}"] / 
                                                                result_df.loc[:,f"ADM{adm_level}_{exp_cat}"]) * 100.0

    # Dropping selected columns for better presentation of the results
    if analysis_type == "Function":
        all_EAI = [col for col in result_df.columns if '_EAI_tmp' in col] if n_valid_RPs_gt_1 else []
        result_df = result_df.drop(all_EAI, axis=1) # dropping
    if analysis_type == "Classes":
        all_EAE = [col for col in result_df.columns if '_EAE_tmp' in col] if n_valid_RPs_gt_1 else []
        result_df = result_df.drop(all_EAE, axis=1) # dropping
        
    return result_df

