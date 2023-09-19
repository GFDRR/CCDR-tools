# Importing the required packages
from common import *
from damageFunctions import damage_factor_FL_builtup, damage_factor_TC_builtup, damage_factor_agri, mortality_factor
from tqdm import tqdm

# Importing the libraries for parallel processing
import itertools as it
from functools import partial
import multiprocess as mp

# Defining functions for parallel processing of zonal_stats
def chunks(data, n):
    """Yield successive n-sized chunks from a slice-able iterable."""
    for i in range(0, len(data), n):
        yield data[i:i+n]

def zonal_stats_partial(feats, raster, stats="*", affine=None, nodata=None, all_touched=True):
    """Partial zonal stats for a parallel processing a list of features"""
    return zonal_stats(feats, raster, stats=stats, affine=affine, nodata=nodata, all_touched=all_touched)

def zonal_stats_parallel(args):
    """Zonal stats for a parallel processing a list of features"""
    return zonal_stats_partial(*args)

# Defining the main function to run the analysis
def run_analysis(country: str, haz_cat: str, valid_RPs: list[int],
                 min_haz_threshold: float, exp_cat: str, exp_nam: str, adm_name: str,
                 analysis_type: str, class_edges: list[float], 
                 save_check_raster: bool, n_cores=None):
    """
    Run specified analysis.

    Parameters
    ----------
    country : country ISO code
    haz_cat : hazard category
    valid_RPs : return period values to be considered
    min_haz_threshold : minimum value for hazard values
    exp_cat : exposure category
    exp_nam : exposure user-specified file name or source
    adm_name : ADM level name
    analysis_type : type of analysis (class or function)
    class_edges : class edges for class-based analysis
    save_check_raster : save intermediate results to disk?
    """
    print("Running analysis...")
    
    # Running the initial checks =======================================================================================
    # Getting the user input variables from run_country into parameters
    adm_name = adm_name.replace('_', '')  # ADM level name

    # Defining the location of administrative, hazard and exposure folders
    adm_folder = f"{DATA_DIR}/ADM"  # Administrative (gpkg) folder
    haz_folder = f"{DATA_DIR}/HZD"  # Hazard folder
    exp_folder = f"{DATA_DIR}/EXP"  # Exposure folder

    # If the analysis type is "Classes", then make sure that the user-defined classes are valid
    bin_seq = None
    num_bins = None
    if analysis_type == "Classes":
        # Ensure class threshold values are valid
        is_seq = np.all([True if class_edges[i] < class_edges[i + 1] else False for i in range(0, len(class_edges) - 1)])
        if not is_seq:
            ValueError(
                "Class thresholds are not sequential. Lower classes must be less than class thresholds above.")
            exit()
        bin_seq = class_edges + [np.inf]
        num_bins = len(bin_seq)
    
    # Checking which kind of exposed category is being considered...
    # If the exposed category is population...
    if exp_cat == 'POP':
        damage_factor = mortality_factor
        exp_ras = f"{exp_folder}/{country}_POP.tif"

    # If the exposed category is builtup area... check hazard type
    elif exp_cat == 'BU':
        if haz_cat == 'FL':
            damage_factor = damage_factor_FL_builtup
        elif haz_cat == 'TC':
            damage_factor = damage_factor_TC_builtup
        exp_ras = f"{exp_folder}/{country}_BU.tif"

    # If the exposed category is agriculture...
    elif exp_cat == 'AGR':
        damage_factor = damage_factor_agri
        exp_ras = f"{exp_folder}/{country}_AGR.tif"
    # If the exposed category is missing, then give an error
    else:
        exp_ras = None
        ValueError(f"Missing or unknown data layer {exp_cat}")
    # If user-specified exposure file name is passed, then
    if exp_nam is not None: 
        exp_cat = str(exp_cat)
        exp_ras = f"{exp_folder}/{country}_{exp_nam}.tif"

    # Running the analysis
    # Importing the exposure data
    exp_data = rxr.open_rasterio(exp_ras)[0]  # Open exposure dataset
    exp_data.rio.write_nodata(-1.0, inplace=True)
    exp_data.data[exp_data < 0.0] = 0.0

    # Loading the ADM data based on country code and adm_name values
    try:
        adm_data = gpd.read_file(os.path.join(f"{adm_folder}/{country}_ADM.gpkg"), layer=f"{country}_{adm_name}")
    except ValueError:
        adm_data = None
        print("Missing ADM layer!")

    # Getting all ADM code/name columns to save with results
    adm_cols = adm_data.columns
    all_adm_codes = adm_data.columns.str.contains("_CODE")
    all_adm_names = adm_data.columns.str.contains("_NAME")
    all_adm_codes = adm_cols[all_adm_codes].to_list()
    all_adm_names = adm_cols[all_adm_names].to_list()
    
    #if n_cores is None: 
    #    cores = min(len(adm_data.index), mp.cpu_count())
    #else:
    #    cores = n_cores
    cores = min(len(adm_data.index), mp.cpu_count())
    with mp.Pool(cores) as p:
        # Get total exposure for each ADM region
        func = partial(zonal_stats_partial, raster=exp_ras, stats="sum")
        stats_parallel = p.map(func, np.array_split(adm_data.geometry, cores))

    exp_per_ADM = list(it.chain(*stats_parallel))

    # Creating the results pandas dataframe
    result_df = adm_data.loc[:, all_adm_codes + all_adm_names + ["geometry"]]
    result_df[f"{adm_name}_{exp_cat}"] = [x['sum'] for x in exp_per_ADM]

    # Cleaning-up memory
    del (stats_parallel, exp_per_ADM)
    gc.collect()
    
    # Defining the list of valid prob_RPs - probability of return period
    prob_RPs = 1./np.array(valid_RPs)
    prob_RPs_LB = np.append(-np.diff(prob_RPs),prob_RPs[-1]).tolist()          # Lower bound - alternative --> prob_RPs_LB = np.append(1-prob_RPs[0],-np.diff(prob_RPs)).tolist() # Lower bound [0-1]
    prob_RPs_UB = np.insert(-np.diff(prob_RPs),0,0.).tolist()                  # Upper bound - alternative --> prob_RPs_UB = np.append(1-prob_RPs[0],-np.diff(prob_RPs)).tolist() # Upper bound [0-1]
    prob_RPs_Mean = ((np.array(prob_RPs_LB)+np.array(prob_RPs_UB))/2).tolist() # Mean value
    prob_RPs_df = pd.DataFrame({'RPs':valid_RPs,
                                'prob_RPs':prob_RPs,
                                'prob_RPs_LB':prob_RPs_LB,
                                'prob_RPs_UB':prob_RPs_UB,
                                'prob_RPs_Mean':prob_RPs_Mean})
    prob_RPs_df.to_csv(os.path.join(OUTPUT_DIR, f"{country}_{haz_cat}_prob_RPs.csv"), index=False)
    
    # Computing the results for each RP
    n_valid_RPs_gt_1 = len(valid_RPs) > 1
    if n_cores is None: 
        cores = min(len(valid_RPs), mp.cpu_count())
    else:
        cores = n_cores
    with mp.Pool(cores) as p:
        params = {
            "haz_folder": haz_folder,
            "analysis_type": analysis_type,
            "country": country,
            "haz_cat": haz_cat,
            "exp_cat": exp_cat,
            "exp_data": exp_data,
            "min_haz_threshold": min_haz_threshold,
            "damage_factor": damage_factor,
            "save_check_raster": save_check_raster,
            "bin_seq": bin_seq,
            "num_bins": num_bins,
            "adm_data": adm_data,
        }
        func = partial(calc_imp_RPs, **params)
        res = p.map(func, np.array_split(valid_RPs, cores))
    if not isinstance(res, list):
        to_concat = [result_df, res]
    else:
        to_concat = [result_df] + res
    result_df = pd.concat(to_concat, axis=1) # Concatenating the results
    result_df = result_df.replace(np.nan, 0) # Converting eventual nan/null to zero
    result_df = result_df_reorder_columns(result_df, valid_RPs, analysis_type, exp_cat, 
                                          adm_name, all_adm_codes, all_adm_names)
    result_df = calc_EAEI(result_df, valid_RPs, prob_RPs_df, 'LB', 
                          analysis_type, country, haz_cat, exp_cat, 
                          adm_name, all_adm_codes, all_adm_names, 
                          save_check_raster, num_bins, n_valid_RPs_gt_1)
    result_df = calc_EAEI(result_df, valid_RPs, prob_RPs_df, 'UB', 
                          analysis_type, country, haz_cat, exp_cat, 
                          adm_name, all_adm_codes, all_adm_names, 
                          save_check_raster, num_bins, n_valid_RPs_gt_1)
    result_df = calc_EAEI(result_df, valid_RPs, prob_RPs_df, 'Mean', 
                          analysis_type, country, haz_cat, exp_cat, 
                          adm_name, all_adm_codes, all_adm_names, 
                          save_check_raster, num_bins, n_valid_RPs_gt_1)
    result_df = result_df.round(3) # Round to three decimal places to avoid giving the impression of high precision
    
    # If method == 'Mean', then simplify it's name
    if n_valid_RPs_gt_1:
        result_df_colnames = result_df.columns.to_list()
        result_df_colnames = [s.replace('_Mean', '') for s in result_df_colnames]
        result_df.set_axis(result_df_colnames, axis=1,inplace=True)
    
    # If not n_valid_RPs_gt_1 and any column contains the initial part as 'RP1_', it is removed then
    if not n_valid_RPs_gt_1:
        result_df_colnames = result_df.columns.to_list()
        result_df_colnames = [s.replace('RP1_', '') for s in result_df_colnames]
        result_df.set_axis(result_df_colnames, axis=1,inplace=True)
    
    # Write output csv table
    df_cols = result_df.columns
    no_geom = result_df.loc[:, df_cols[~df_cols.isin(['geometry'])]].fillna(0)
    file_prefix = f"{country}_{adm_name}_{haz_cat}_{exp_cat}"
    if analysis_type == "Function":
        if len(valid_RPs) > 1:
            no_geom.to_csv(os.path.join(OUTPUT_DIR, f"{file_prefix}_EAI_function.csv"), index=False)
            result_df.to_file(os.path.join(OUTPUT_DIR, f"{file_prefix}_EAI_function.gpkg"))
        else:
            no_geom.to_csv(os.path.join(OUTPUT_DIR, f"{file_prefix}_function.csv"), index=False)
            result_df.to_file(os.path.join(OUTPUT_DIR, f"{file_prefix}_function.gpkg"))
    elif analysis_type == "Classes":
        if len(valid_RPs) > 1:
            no_geom.to_csv(os.path.join(OUTPUT_DIR, f"{file_prefix}_EAE_class.csv"), index=False)
            result_df.to_file(os.path.join(OUTPUT_DIR, f"{file_prefix}_EAE_class.gpkg"))
        else:
            no_geom.to_csv(os.path.join(OUTPUT_DIR, f"{file_prefix}_class.csv"), index=False)
            result_df.to_file(os.path.join(OUTPUT_DIR, f"{file_prefix}_class.gpkg"))

    # Cleaning-up memory
    del (country, haz_cat, valid_RPs, min_haz_threshold, exp_cat, adm_name)
    del (analysis_type, class_edges, save_check_raster)
    del (adm_folder, haz_folder, exp_folder)
    del (exp_ras, exp_data)
    del (adm_data, adm_cols, all_adm_codes, all_adm_names)
    del (result_df)

    # Finishing the analysis
    print("Finished analysis.")


def calc_imp_RPs(RPs, haz_folder, analysis_type, country, haz_cat, exp_cat, exp_data, min_haz_threshold,
                 damage_factor, save_check_raster, bin_seq, num_bins, adm_data):
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
            with rasterio.open(os.path.join(haz_folder, f"{country}_{haz_cat}_RP{rp}.tif")) as src:
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
            raise IOError(f"Error occurred trying to open raster file: {country}_{haz_cat}_RP{rp}.tif")

        # Set values below min threshold to nan
        haz_data = haz_data.where(haz_data.data > min_haz_threshold, np.nan)
        
        # Checking the analysis_type
        if analysis_type == "Function":
            # Assign impact factor (this is F_i in the equations)
            haz_data = damage_factor(haz_data)
            if save_check_raster:
                haz_data.rio.to_raster(os.path.join(OUTPUT_DIR, f"{country}_{haz_cat}_{rp}_{exp_cat}_haz_imp_factor.tif"))
        elif analysis_type == "Classes":
            # Assign bin values to raster data - Follows: x_{i-1} <= x_{i} < x_{i+1}
            bin_idx = np.digitize(haz_data, bin_seq)

        # Calculate affected exposure in ADM
        # Filter down to valid areas affected areas which have people
        affected_exp = exp_data.where(haz_data.data > 0, np.nan)

        if save_check_raster:
            affected_exp.rio.to_raster(os.path.join(OUTPUT_DIR, f"{country}_{haz_cat}_{exp_cat}_{rp}_affected.tif"))
        
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
                impact_exp.rio.to_raster(os.path.join(OUTPUT_DIR, f"{country}_{haz_cat}_{exp_cat}_{rp}_impact.tif"))
            # Compute the impact per ADM level
            impact_exp_per_ADM = gen_zonal_stats(vectors=adm_data["geometry"], raster=impact_exp.data, stats=["sum"],
                                                 affine=impact_exp.rio.transform(), nodata=np.nan)
            result_df[f"RP{rp}_{exp_cat}_imp"] = [x['sum'] for x in impact_exp_per_ADM]
            del (haz_data, impact_exp, impact_exp_per_ADM, affected_exp_per_ADM)

        del affected_exp
        gc.collect()

    return result_df


def result_df_reorder_columns(result_df, RPs, analysis_type, exp_cat, adm_name, all_adm_codes, all_adm_names):
    """
    Reorders the columns of result_df.
    """
    # Re-ordering and dropping selected columns for better presentation of the results
    if analysis_type == "Function":
        all_RPs = ["RP" + str(rp) for rp in RPs]
        all_exp = [x + f"_{exp_cat}_exp" for x in all_RPs]
        all_imp = [x + f"_{exp_cat}_imp" for x in all_RPs]
        col_order = all_adm_codes + all_adm_names + [f"{adm_name}_{exp_cat}"] + all_exp + all_imp
        col_order += ["geometry"]
        result_df = result_df.loc[:, col_order]
        
    # if analysis_type == "Classes":
    
    return result_df

def calc_EAEI(result_df, RPs, prob_RPs_df, method, analysis_type, country, haz_cat, exp_cat, 
              adm_name, all_adm_codes, all_adm_names, save_check_raster, num_bins, n_valid_RPs_gt_1):
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
                    EAI_i.rio.to_raster(os.path.join(OUTPUT_DIR, f"{country}_{haz_cat}_{exp_cat}_{rp}_EAI.tif"))
        
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
                                                                         result_df.loc[:,f"{adm_name}_{exp_cat}"]) * 100.0
        # Computing EAI if analysis is Function
        if analysis_type == "Function":
            if n_valid_RPs_gt_1:
                # Sum all EAI to get total EAI across all RPs
                result_df.loc[:, f"{exp_cat}_EAI_{method}"] = result_df.loc[:,result_df.columns.str.contains('_EAI_tmp')].sum(axis=1)
                # Calculate Exp_EAI% (Percent affected exposure per year)
                result_df.loc[:, f"{exp_cat}_EAI%_{method}"] = (result_df.loc[:, f"{exp_cat}_EAI_{method}"] / 
                                                                result_df.loc[:,f"{adm_name}_{exp_cat}"]) * 100.0

    # Dropping selected columns for better presentation of the results
    if analysis_type == "Function":
        all_EAI = [col for col in result_df.columns if '_EAI_tmp' in col] if n_valid_RPs_gt_1 else []
        result_df = result_df.drop(all_EAI, axis=1) # dropping
    if analysis_type == "Classes":
        all_EAE = [col for col in result_df.columns if '_EAE_tmp' in col] if n_valid_RPs_gt_1 else []
        result_df = result_df.drop(all_EAE, axis=1) # dropping
        
    return result_df

