# Importing the required packages
import sys
from common import *
from damageFunctions import damage_factor_builtup, damage_factor_agri, mortality_factor
from runAnalysis import run_analysis

# Defining the main function
def main():
    # Defining the initial parameters
    country_dd         = 'KHM'
    haz_cat_dd         = 'FL' #'FL' for floods; 'HS' for heat stress; 'DR' for drought; 'LS' for landslide
    return_periods     = [5, 10, 20, 50, 75, 100, 200, 250, 500, 1000] # FL [5, 10, 20, 50, 75, 100, 200, 250, 500, 1000] # TC [10, 20, 50, 100, 200, 500] # add here as will
    min_haz_slider     = 0.05 # FL 0.05 # TC 25.0 # ASI 0.01
    exp_cat_dd_list    = ['pop', 'builtup', 'agri'] # ['pop', 'builtup', 'agri']
    exp_nam_dd_list    = ['WPOP20', 'WSF19', 'ESA20_agri']
                         # if None, the default applies: 'pop':'WPOP20', 'builtup':'WSF19', 'agri':'ESA20_agri', 'cstk'.'CSTK19' - If not None, expect a list of same length of exp_cat_dd_list
    adm_dd             = 'ADM3' #['ADM1', 'ADM2', 'ADM3']
    analysis_app_dd    = 'Classes' #['Classes', 'Function']
    class_edges        = [0.05, 0.25, 0.50, 1.00, 2.00] # FL [0.05, 0.25, 0.50, 1.00, 2.00] # TC [17.0, 32.0, 42.0, 49.0, 58.0, 70.0] # DR_ASI [0.01, 0.10, 0.25, 0.40, 0.55, 0.70, 0.85]
    save_check_raster  = False

    import time
    start_time = time.time()

    # Running the analysis
    if exp_nam_dd_list is not None and len(exp_nam_dd_list) != len(exp_cat_dd_list): sys.exit("ERROR: Parameter 'exp_nam_dd_list' should either be 'None' or have the same length as 'exp_cat_dd_list'")
    # For every exp_cat_dd
    for i in range(len(exp_cat_dd_list)):
        # Defining the list variable to pass to run_analysis
        exp_cat_dd = exp_cat_dd_list[i]
        exp_nam_dd = exp_nam_dd_list[i]
        run_analysis(country_dd, haz_cat_dd, return_periods, min_haz_slider, exp_cat_dd, exp_nam_dd, adm_dd, analysis_app_dd, class_edges, save_check_raster)

    print("--- %s seconds ---" % (time.time() - start_time))

if __name__ == "__main__":
    sys.exit(main())
