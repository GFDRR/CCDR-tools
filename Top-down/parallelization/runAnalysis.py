# Importing the required packages
from common import *
from damageFunctions import damage_factor_builtup, damage_factor_agri, mortality_factor

# Importing the libraries for parallel processing
import itertools as it
from functools import partial
import multiprocess as mp

import time


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
def run_analysis(run_country):
    print("Running analysis...")

    # Running the initial checks =======================================================================================
    # Getting the user input variables from run_country into parameters
    country = run_country[0]  # country ISO code
    haz_cat = run_country[1]  # hazard category
    valid_RPs = run_country[2]  # return period values to be considered
    min_haz_threshold = run_country[3]  # minimum value for hazard values
    exp_cat = run_country[4]  # exposure category
    adm_name = run_country[5].replace('_', '')  # ADM level name
    time_horizon = run_country[6]  # time horizon to be considered
    rcp_scenario = run_country[7]  # rcp scenario to be considered
    analysis_type = run_country[8]  # type of analysis (class or function?)
    class_edges = run_country[9]  # class edges for class-based analysis
    save_inter_rst_chk = run_country[10]  # save intermediate results to disk?

    # Defining the location of administrative, hazard and exposure folders
    adm_folder = f"{DATA_DIR}/ADM"  # Administrative (gpkg) folder
    haz_folder = f"{DATA_DIR}/HZD"  # Hazard folder
    exp_folder = f"{DATA_DIR}/EXP"  # Exposure folder

    # If the analysis type is "Classes", then make sure that the user-defined classes are valid
    if analysis_type == "Classes":
        # Ensure class threshold values are valid
        seq_check = np.all([True if class_edges[i] < class_edges[i + 1] else False for i in range(0, len(class_edges) - 1)])

        if not seq_check:
            ValueError("Class thresholds are not sequential. Lower classes must be less than class thresholds above.")
            exit()

        max_bin_value = np.max(class_edges)
        max_haz_threshold = np.max(class_edges) + 1e-4
        bin_seq = class_edges + [np.inf]
        num_bins = len(bin_seq)

    # Testing data file locations
    # TODO: Temp data store, to be replaced with a config spec (.env file?) before deployment

    # Checking which kind of exposed category is being considered...
    # If the exposed category is population...
    if exp_cat == 'pop':
        damage_factor = mortality_factor
        exp_ras = f"{exp_folder}/{country}_WPOP20.tif"
    # If the exposed category is builtup area...
    elif exp_cat == 'builtup':
        damage_factor = damage_factor_builtup
        exp_ras = f"{exp_folder}/{country}_WSF19.tif"
    # If the exposed category is agriculture...
    elif exp_cat == 'agri':
        damage_factor = damage_factor_agri
        exp_ras = f"{exp_folder}/{country}_ESA20_agri.tif"
    # If the exposed category is capital stock...
    elif exp_cat == 'cstk':
        damage_factor = damage_factor_builtup
        exp_ras = f"{exp_folder}/{country}_CSTK19.tif"
    # If the exposed category is missing, then give an error
    else:
        exp_ras = None
        ValueError(f"Missing or unknown data layer {exp_cat}")

    # Cleaning-up memory
    gc.collect()
    # ==================================================================================================================

    # Running the analysis =============================================================================================
    # Importing the exposure data
    exp_data = rxr.open_rasterio(exp_ras)  # Open exposure dataset
    exp_data.rio.write_nodata(-1, inplace=True)  # Indicate -1 values as representing no data

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
    
    # Creating the results pandas dataframe
    result_df = adm_data.loc[:, all_adm_codes + all_adm_names + ["geometry"]]

    # Creating a process pool using all cores
    # cores = mp.cpu_count()
    cores = 4
    with mp.Pool(cores) as p:
        # Get total exposure for each ADM region
        func = partial(zonal_stats_partial, raster=exp_ras, stats="sum")
        stats_parallel = p.map(func, np.array_split(adm_data.geometry, cores))
        # stats_parallel = p.imap(func, zip(chunks(adm_data.geometry, cores)))

    exp_per_ADM = list(it.chain(*stats_parallel))
    result_df[f"{adm_name}_{exp_cat}"] = [x['sum'] for x in exp_per_ADM]

    # Cleaning-up memory
    del (stats_parallel, exp_per_ADM)
    # gc.collect()

    # For every probability as defined in the return period vector
    for rp in valid_RPs:
        # Probability of return period
        # Essentially the same as 1/RP, but accounts for cases where RP == 1
        st = time.time()
        freq = 1 - np.exp(-1 / rp)

        # Loading the corresponding hazard dataset
        try:
            haz_data = rxr.open_rasterio(os.path.join(haz_folder, f"{country}_{haz_cat}_RP{rp}.tif"))

            # Reproject and clip raster to same bounds as exposure data
            haz_data = haz_data.rio.reproject_match(exp_data)
        except rxr._err.CPLE_OpenFailedError:
            raise(IOError, f"Error occurred trying to open raster file: {country}_{haz_cat}_RP{rp}.tif")
        
        # Get raw array values for exposure and hazard layer
        haz_array = haz_data[0].values
        haz_array[haz_array < min_haz_threshold] = np.nan  # Set values below min threshold to nan
        # Checking the analysis_type
        if analysis_type == "Function":
            # Assign impact factor (this is F_i)
            impact_arr = damage_factor(haz_array)

            # Create raster from array
            impact_rst = xr.DataArray(np.array([impact_arr]).astype(np.float32), coords=haz_data.coords,
                                      dims=haz_data.dims)

            # If save intermediate to disk is TRUE, then
            if save_inter_rst_chk:
                impact_rst.rio.to_raster(
                    os.path.join(OUTPUT_DIR, f"{country}_{haz_cat}_{rp}_{exp_cat}_haz_imp_factor.tif"))
        elif analysis_type == "Classes":
            # Pre-process the haz_array data
            haz_array[np.isnan(haz_array)] = 0  # Set NaNs to 0
            haz_array[haz_array > max_bin_value] = max_haz_threshold  # Cap large values to maximum threshold value

            # Assign bin values to raster data
            # Follows: x_{i-1} <= x_{i} < x_{i+1}
            bin_idx = np.digitize(haz_array, bin_seq)
            impact_arr = None
            impact_rst = haz_data

        dt = time.time()
        # Calculate affected exposure in ADM
        # Filter down to valid areas
        valid_impact_areas = impact_rst.values > 0
        affected_exp = exp_data.where(valid_impact_areas)  # Get total exposure in affected areas
        affected_exp = affected_exp.where(affected_exp > 0)  # Out of the above, get areas that have people

        if save_inter_rst_chk:
            affected_exp.rio.to_raster(os.path.join(OUTPUT_DIR, f"{country}_{haz_cat}_{exp_cat}_{rp}_affected.tif"))

        # Cleaning-up memory
        del (haz_data, haz_array, impact_arr)
        # gc.collect()

        print("Time taken to filter and save affected rst:", time.time() - dt)

        # Conduct analyses for classes
        if analysis_type == "Classes":
            for bin_x in reversed(range(0, num_bins)):
                # Compute the impact for this class
                impact_class = gen_zonal_stats(vectors=adm_data["geometry"],
                                               raster=np.array(bin_idx == bin_x).astype(int) * affected_exp.data[0],
                                               stats=["sum"], affine=affected_exp.rio.transform(), nodata=np.nan)
                result_df[f"RP{rp}_{exp_cat}_C{bin_x}"] = [x['sum'] for x in impact_class]
                # Compute the cumulative impact for this class
                if bin_x < (num_bins - 1):
                    result_df[f"RP{rp}_{exp_cat}_C{bin_x}"] = result_df[f"RP{rp}_{exp_cat}_C{bin_x}"] + result_df[
                        f"RP{rp}_{exp_cat}_C{bin_x + 1}"]
                # Cleaning-up memory
                del impact_class
                # gc.collect()
            # end

            # Compute the EAE for classes, if probabilistic (len(valid_RPs)>1)
            if len(valid_RPs) > 1:
                for bin_x in reversed(range(0, num_bins)):
                    result_df[f"RP{rp}_{exp_cat}_C{bin_x}_EAE"] = result_df[f"RP{rp}_{exp_cat}_C{bin_x}"] * freq

        # Conduct analyses for function
        if analysis_type == "Function":
            # Calculate degree of impact over Exposure category
            impact_exp = affected_exp * impact_rst.where(valid_impact_areas)  # Get impacted exposure in affected areas

            # If save intermediate to disk is TRUE, then
            if save_inter_rst_chk:
                impact_exp.rio.to_raster(os.path.join(OUTPUT_DIR, f"{country}_{haz_cat}_{exp_cat}_{rp}_impact.tif"))

            # Compute the impact per ADM level
            impact_exp_per_ADM = gen_zonal_stats(vectors=adm_data["geometry"], raster=impact_exp.data[0], stats=["sum"],
                                                 affine=impact_exp.rio.transform(), nodata=0)
            result_df[f"RP{rp}_{exp_cat}_imp"] = [x['sum'] for x in impact_exp_per_ADM]

            # Compute the exposure per ADM level
            affected_exp_per_ADM = gen_zonal_stats(vectors=adm_data["geometry"], raster=affected_exp.data[0],
                                                   stats=["sum"], affine=affected_exp.rio.transform(), nodata=0)
            result_df[f"RP{rp}_{exp_cat}_tot"] = [x['sum'] for x in affected_exp_per_ADM]

            # Compute the EAI for this RP, if probabilistic (len(valid_RPs)>1)
            if len(valid_RPs) > 1:
                result_df[f"RP{rp}_EAI"] = result_df[f"RP{rp}_{exp_cat}_imp"] * freq
                # If save intermediate to disk is TRUE, then
                if save_inter_rst_chk:
                    EAI_i = impact_exp.where(valid_impact_areas) * freq
                    EAI_i.rio.to_raster(os.path.join(OUTPUT_DIR, f"{country}_{haz_cat}_{exp_cat}_{rp}_EAI.tif"))
                    del EAI_i
                    # gc.collect()

            # Cleaning-up memory
            del (impact_exp, impact_exp_per_ADM, affected_exp_per_ADM)
            # gc.collect()

        # Cleaning-up memory
        del (impact_rst, affected_exp, valid_impact_areas)

        print("Time to do 1 RP:", time.time() - st)
        breakpoint()

    # End RP loop

    # Computing the EAE or EAI, if probabilistic (len(valid_RPs)>1)
    if len(valid_RPs) > 1:
        # Computing EAE if analysis is Classes
        if analysis_type == "Classes":
            # Sum all EAI to get total EAI across all RPs and Classes
            for bin_x in reversed(range(0, num_bins)):
                C_EAE_cols = result_df.columns.str.contains(f"{exp_cat}_C{bin_x}_EAE")
                result_df.loc[:, f"{exp_cat}_C{bin_x}_EAE"] = result_df.loc[:, C_EAE_cols].sum(axis=1)
            # Calculate EAE% (Percent affected exposure per year)
            for bin_x in reversed(range(0, num_bins)):
                result_df.loc[:, f"{exp_cat}_C{bin_x}_EAE%"] = (result_df.loc[:,
                                                                f"{exp_cat}_C{bin_x}_EAE"] / result_df.loc[:,
                                                                                             f"{adm_name}_{exp_cat}"]) * 100.0
        # Computing EAI if analysis is Function
        if analysis_type == "Function":
            # Sum all EAI to get total EAI across all RPs
            result_df.loc[:, f"{exp_cat}_EAI"] = result_df.loc[:, result_df.columns.str.contains('_EAI')].sum(axis=1)
            # Calculate Exp_EAI% (Percent affected exposure per year)
            result_df.loc[:, f"{exp_cat}_EAI%"] = (result_df.loc[:, f"{exp_cat}_EAI"] / result_df.loc[:,
                                                                                        f"{adm_name}_{exp_cat}"]) * 100.0

    # Converting eventual nan/null to zero
    result_df = result_df.replace(np.nan, 0)

    # Re-ordering the columns for better presentation of the results
    if analysis_type == "Function":
        # Reorder the columns of result_df
        all_RPs = ["RP" + str(rp) for rp in valid_RPs]
        all_exp = [x + f"_{exp_cat}_tot" for x in all_RPs]
        all_imp = [x + f"_{exp_cat}_imp" for x in all_RPs]
        all_EAI = []
        if len(valid_RPs) > 1:
            all_EAI = [x + "_EAI" for x in all_RPs]
        col_order = all_adm_codes + all_adm_names + [f"{adm_name}_{exp_cat}"] + all_exp + all_imp + all_EAI + [
            f"{exp_cat}_EAI", f"{exp_cat}_EAI%", "geometry"]
        result_df = result_df.loc[:, col_order]

    # Round to three decimal places to avoid giving the impression of high precision
    result_df = result_df.round(3)

    # Write table of total exposure in each class, in each ADM level
    df_cols = result_df.columns
    no_geom = result_df.loc[:, df_cols[~df_cols.isin(['geometry'])]].fillna(0)
    if analysis_type == "Function":
        if len(valid_RPs) > 1:
            no_geom.to_csv(os.path.join(OUTPUT_DIR, f"{country}_{haz_cat}_{adm_name}_{exp_cat}_EAI.csv"), index=False)
            result_df.to_file(os.path.join(OUTPUT_DIR, f"{country}_{haz_cat}_{adm_name}_{exp_cat}_EAI_function.gpkg"))
        else:
            no_geom.to_csv(os.path.join(OUTPUT_DIR, f"{country}_{haz_cat}_{adm_name}_{exp_cat}.csv"), index=False)
            result_df.to_file(os.path.join(OUTPUT_DIR, f"{country}_{haz_cat}_{adm_name}_{exp_cat}_function.gpkg"))
    elif analysis_type == "Classes":
        if len(valid_RPs) > 1:
            no_geom.to_csv(os.path.join(OUTPUT_DIR, f"{country}_{haz_cat}_{adm_name}_{exp_cat}_EAE_class.csv"), index=False)
            result_df.to_file(os.path.join(OUTPUT_DIR, f"{country}_{haz_cat}_{adm_name}_{exp_cat}_EAE_class.gpkg"))
        else:
            no_geom.to_csv(os.path.join(OUTPUT_DIR, f"{country}_{haz_cat}_{adm_name}_{exp_cat}_class.csv"), index=False)
            result_df.to_file(os.path.join(OUTPUT_DIR, f"{country}_{haz_cat}_{adm_name}_{exp_cat}_class.gpkg"))

    # Cleaning-up memory
    del (country, haz_cat, valid_RPs, min_haz_threshold, exp_cat, adm_name)
    del (time_horizon, rcp_scenario, analysis_type, class_edges, save_inter_rst_chk)
    del (adm_folder, haz_folder, exp_folder)
    del (exp_ras, exp_data)
    del (adm_data, adm_cols, all_adm_codes, all_adm_names)
    del (result_df)
    # gc.collect()

    # Finishing the analysis
    print("Finished analysis.")
