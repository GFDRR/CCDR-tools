# Importing the required packages
from common import *
from damageFunctions import damage_factor_builtup, damage_factor_agri, mortality_factor

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
                 min_haz_threshold: float, exp_cat: str, adm_name: str,
                 time_horizon: list[int], rcp_scenario: list[str],
                 analysis_type: str, class_edges: list[float], 
                 save_check_raster: bool, cores: int=1):
    """
    Run specified analysis.

    Parameters
    ----------
    country : country ISO code
    haz_cat : hazard category
    valid_RPs : return period values to be considered
    min_haz_threshold : minimum value for hazard values
    exp_cat : exposure category
    adm_name : ADM level name
    time_horizon : time horizon to be considered
    rcp_scenario : rcp scenario to be considered
    analysis_type : type of analysis (class or function)
    class_edges : class edges for class-based analysis
    save_check_raster : save intermediate results to disk?
    cores : number of cores to use for parallel processing (default: 1, no parallelization)
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
    max_bin_value = None
    max_haz_threshold = None
    bin_seq = None
    num_bins = None
    if analysis_type == "Classes":
        # Ensure class threshold values are valid
        is_seq = np.all([True if class_edges[i] < class_edges[i + 1]
                           else False for i in range(0, len(class_edges) - 1)])

        if not is_seq:
            ValueError(
                "Class thresholds are not sequential. Lower classes must be less than class thresholds above.")
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

    # Running the analysis
    # Importing the exposure data
    exp_data = rxr.open_rasterio(exp_ras)[0]  # Open exposure dataset
    exp_data.rio.write_nodata(-1.0, inplace=True)
    exp_data.data[exp_data < 0.0] = 0.0

    # Loading the ADM data based on country code and adm_name values
    try:
        adm_data = gpd.read_file(os.path.join(
            f"{adm_folder}/{country}_ADM.gpkg"), layer=f"{country}_{adm_name}")
    except ValueError:
        adm_data = None
        print("Missing ADM layer!")

    # Getting all ADM code/name columns to save with results
    adm_cols = adm_data.columns
    all_adm_codes = adm_data.columns.str.contains("_CODE")
    all_adm_names = adm_data.columns.str.contains("_NAME")
    all_adm_codes = adm_cols[all_adm_codes].to_list()
    all_adm_names = adm_cols[all_adm_names].to_list()

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

    n_valid_RPs_gt_1 = len(valid_RPs) > 1
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
            "max_bin_value": max_bin_value,
            "max_haz_threshold": max_haz_threshold,
            "bin_seq": bin_seq,
            "num_bins": num_bins,
            "adm_data": adm_data,
            "n_valid_RPs_gt_1": n_valid_RPs_gt_1
        }

        func = partial(calc_RPs, **params)
        res = p.map(func, np.array_split(valid_RPs, cores))

    if not isinstance(res, list):
        to_concat = [result_df, res]
    else:
        to_concat = [result_df] + res

    result_df = pd.concat(to_concat, axis=1)

    # Computing the EAE or EAI, if probabilistic (len(valid_RPs)>1)
    if len(valid_RPs) > 1:
        # Computing EAE if analysis is Classes
        if analysis_type == "Classes":
            # Sum all EAI to get total EAI across all RPs and Classes
            for bin_x in reversed(range(0, num_bins)):
                C_EAE_cols = result_df.columns.str.contains(
                    f"{exp_cat}_C{bin_x}_EAE")
                result_df.loc[:, f"{exp_cat}_C{bin_x}_EAE"] = result_df.loc[:, C_EAE_cols].sum(
                    axis=1)

            # Calculate EAE% (Percent affected exposure per year)
            for bin_x in reversed(range(0, num_bins)):
                result_df.loc[:, f"{exp_cat}_C{bin_x}_EAE%"] = (result_df.loc[:,
                                                                f"{exp_cat}_C{bin_x}_EAE"] / result_df.loc[:,
                                                                                                           f"{adm_name}_{exp_cat}"]) * 100.0
        # Computing EAI if analysis is Function
        if analysis_type == "Function":
            if len(valid_RPs) > 1:
                # Sum all EAI to get total EAI across all RPs
                result_df.loc[:, f"{exp_cat}_EAI"] = result_df.loc[:,
                                                                result_df.columns.str.contains('_EAI')].sum(axis=1)
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
        all_EAI = [x + "_EAI" for x in all_RPs] if len(valid_RPs) > 1 else []

        col_order = all_adm_codes + all_adm_names + [f"{adm_name}_{exp_cat}"] + \
            all_exp + all_imp + all_EAI
        
        if len(valid_RPs) > 1:
            col_order += [f"{exp_cat}_EAI", f"{exp_cat}_EAI%"]
        
        col_order += ["geometry"]

        result_df = result_df.loc[:, col_order]

    # Round to three decimal places to avoid giving the impression of high precision
    result_df = result_df.round(3)

    # Write table of total exposure in each class, in each ADM level
    df_cols = result_df.columns
    no_geom = result_df.loc[:, df_cols[~df_cols.isin(['geometry'])]].fillna(0)
    file_prefix = f"{country}_{haz_cat}_{adm_name}_{exp_cat}"
    if analysis_type == "Function":
        if len(valid_RPs) > 1:
            no_geom.to_csv(os.path.join(
                OUTPUT_DIR, f"{file_prefix}_EAI.csv"), index=False)
            result_df.to_file(os.path.join(
                OUTPUT_DIR, f"{file_prefix}_EAI_function.gpkg"))
        else:
            no_geom.to_csv(os.path.join(
                OUTPUT_DIR, f"{file_prefix}.csv"), index=False)
            result_df.to_file(os.path.join(
                OUTPUT_DIR, f"{file_prefix}_function.gpkg"))
    elif analysis_type == "Classes":
        if len(valid_RPs) > 1:
            no_geom.to_csv(os.path.join(
                OUTPUT_DIR, f"{file_prefix}_EAE_class.csv"), index=False)
            result_df.to_file(os.path.join(
                OUTPUT_DIR, f"{file_prefix}_EAE_class.gpkg"))
        else:
            no_geom.to_csv(os.path.join(
                OUTPUT_DIR, f"{file_prefix}_class.csv"), index=False)
            result_df.to_file(os.path.join(
                OUTPUT_DIR, f"{file_prefix}_class.gpkg"))

    # Cleaning-up memory
    del (country, haz_cat, valid_RPs, min_haz_threshold, exp_cat, adm_name)
    del (time_horizon, rcp_scenario, analysis_type,
         class_edges, save_check_raster)
    del (adm_folder, haz_folder, exp_folder)
    del (exp_ras, exp_data)
    del (adm_data, adm_cols, all_adm_codes, all_adm_names)
    del (result_df)

    # Finishing the analysis
    print("Finished analysis.")


def calc_RPs(RP, haz_folder, analysis_type, country, haz_cat, exp_cat, exp_data, min_haz_threshold,
             damage_factor, save_check_raster, max_bin_value, max_haz_threshold, bin_seq, num_bins, adm_data, n_valid_RPs_gt_1):
    """
    Apply calculates for each given return period.
    """
    result_df = pd.DataFrame()
    for rp in RP:

        # Probability of return period
        # Essentially the same as 1/RP, but accounts for cases where RP == 1
        freq = 1 - np.exp(-1 / rp)

        # Loading the corresponding hazard dataset
        try:
            # reproject_match, while useful, uses ~6-8GB!
            # haz_data = xr.open_rasterio(os.path.join(haz_folder, f"{country}_{haz_cat}_RP{rp}.tif"))
            # haz_data.rio.write_nodata(-1.0, inplace=True)
            # haz_data = haz_data.rio.reproject_match(exp_data)[0]

            # Instead, we reproject using WarpedVRT as this applies the operation from disk
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

        except rxr._err.CPLE_OpenFailedError:
            raise IOError(
                f"Error occurred trying to open raster file: {country}_{haz_cat}_RP{rp}.tif")

        # Set values below min threshold to nan
        haz_data = haz_data.where(haz_data.data > min_haz_threshold, np.nan)

        # Checking the analysis_type
        if analysis_type == "Function":
            # Assign impact factor (this is F_i in the equations)
            impact_rst = damage_factor(haz_data)

            if save_check_raster:
                impact_rst.rio.to_raster(
                    os.path.join(OUTPUT_DIR, f"{country}_{haz_cat}_{rp}_{exp_cat}_haz_imp_factor.tif"))

        elif analysis_type == "Classes":
            # Pre-process the haz_array data
            # haz_data[np.isnan(haz_data)] = 0  # Set NaNs to 0

            # Cap large values to maximum threshold value
            haz_data = haz_data.where(haz_data > max_haz_threshold, np.nan)

            # Assign bin values to raster data
            # Follows: x_{i-1} <= x_{i} < x_{i+1}
            bin_idx = np.digitize(haz_data, bin_seq)
            impact_rst = haz_data

        # Calculate affected exposure in ADM
        # Filter down to valid areas affected areas which have people
        affected_exp = exp_data.where(impact_rst.data > 0.0, np.nan)

        if save_check_raster:
            affected_exp.rio.to_raster(os.path.join(
                OUTPUT_DIR, f"{country}_{haz_cat}_{exp_cat}_{rp}_affected.tif"))

        del haz_data
        gc.collect()

        # Conduct analyses for classes
        if analysis_type == "Classes":
            for bin_x in reversed(range(num_bins)):
                # Compute the impact for this class
                impact_class = gen_zonal_stats(vectors=adm_data["geometry"],
                                               raster=np.array(bin_idx == bin_x).astype(
                    int) * affected_exp,
                    stats=["sum"], affine=affected_exp.rio.transform(), nodata=np.nan)
                result_df[f"RP{rp}_{exp_cat}_C{bin_x}"] = [x['sum']
                                                           for x in impact_class]
                # Compute the cumulative impact for this class
                if bin_x < (num_bins - 1):
                    result_df[f"RP{rp}_{exp_cat}_C{bin_x}"] = result_df[f"RP{rp}_{exp_cat}_C{bin_x}"] + \
                        result_df[f"RP{rp}_{exp_cat}_C{bin_x + 1}"]

                del impact_class
            # end

            # Compute the EAE for classes, if probabilistic (len(valid_RPs)>1)
            if n_valid_RPs_gt_1:
                for bin_x in reversed(range(num_bins)):
                    result_df[f"RP{rp}_{exp_cat}_C{bin_x}_EAE"] = result_df[f"RP{rp}_{exp_cat}_C{bin_x}"] * freq

        # Conduct analyses for function
        if analysis_type == "Function":
            # Calculate degree of impact over Exposure category
            # Get impacted exposure in affected areas
            impact_exp = affected_exp.data * impact_rst
            del impact_rst

            # If save intermediate to disk is TRUE, then
            if save_check_raster:
                impact_exp.rio.to_raster(os.path.join(
                    OUTPUT_DIR, f"{country}_{haz_cat}_{exp_cat}_{rp}_impact.tif"))

            # Compute the impact per ADM level
            impact_exp_per_ADM = gen_zonal_stats(vectors=adm_data["geometry"], raster=impact_exp.data, stats=["sum"],
                                                 affine=impact_exp.rio.transform(), nodata=np.nan)
            result_df[f"RP{rp}_{exp_cat}_imp"] = [x['sum'] for x in impact_exp_per_ADM]

            # Compute the exposure per ADM level
            affected_exp_per_ADM = gen_zonal_stats(vectors=adm_data["geometry"], raster=affected_exp.data,
                                                   stats=["sum"], affine=affected_exp.rio.transform(), nodata=np.nan)
            result_df[f"RP{rp}_{exp_cat}_tot"] = [x['sum'] for x in affected_exp_per_ADM]

            # Compute the EAI for this RP, if probabilistic (len(valid_RPs)>1)
            if n_valid_RPs_gt_1:
                result_df[f"RP{rp}_EAI"] = result_df[f"RP{rp}_{exp_cat}_imp"] * freq

                if save_check_raster:
                    EAI_i = impact_exp * freq
                    EAI_i.rio.to_raster(os.path.join(
                        OUTPUT_DIR, f"{country}_{haz_cat}_{exp_cat}_{rp}_EAI.tif"))
                    del EAI_i

            del (impact_exp, impact_exp_per_ADM, affected_exp_per_ADM)

        del affected_exp

        gc.collect()

    return result_df