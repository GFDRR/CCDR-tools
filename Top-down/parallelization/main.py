# Importing the required packages
import sys
from common import *
from damageFunctions import damage_factor_builtup, damage_factor_agri, mortality_factor
from runAnalysis import run_analysis

# Defining the main function
def main():
    # Defining the initial parameters
    country         = 'BGD'			  # ISO3166-a3 code
    haz_cat         = 'FL' 			  #'FL' for floods; 'HS' for heat stress; 'DR' for drought; 'LS' for landslide
    return_periods     = [5, 10, 20, 50, 75, 100, 200, 250, 500, 1000] # FL [5, 10, 20, 50, 75, 100, 200, 250, 500, 1000] # TC [10, 20, 50, 100, 200, 500] # add here as will
    min_haz_slider     = 0.05 			  # FL 0.05 # TC 25.0 # ASI 0.01
    exp_cat_list    = ['pop', 'BU', 'AGR']	  # ['pop', 'builtup', 'agri']
    exp_nam_list    = ['POP', 'BU', 'AGR']	  # if None, the default applies: 'Population':'POP', 'Built-up':'BU', 'Agricultural land':'AGR' - If not None, expect a list of same length of exp_cat_list
    adm             = 'ADM3' 			  #['ADM1', 'ADM2', 'ADM3']
    analysis_app    = 'Function'		  #['Classes', 'Function']
    class_edges        = [0.05, 0.25, 0.50, 1.00, 2.00] # FL [0.05, 0.25, 0.50, 1.00, 2.00] # TC [17.0, 32.0, 42.0, 49.0, 58.0, 70.0] # DR_ASI [0.01, 0.10, 0.25, 0.40, 0.55, 0.70, 0.85]
    save_check_raster  = False

    import time
    start_time = time.time()

    # Running the analysis
    if exp_nam_list is not None and len(exp_nam_list) != len(exp_cat_list): sys.exit("ERROR: Parameter 'exp_nam_list' should either be 'None' or have the same length as 'exp_cat_list'")
    # For every exp_cat
    for i in range(len(exp_cat_list)):
        # Defining the list variable to pass to run_analysis
        exp_cat = exp_cat_list[i]
        exp_nam = exp_nam_list[i]
        run_analysis(country, haz_cat, return_periods, min_haz_slider,
                       exp_cat, exp_nam, adm, analysis_app, class_edges, save_check_raster)

    print("--- %s seconds ---" % (time.time() - start_time))

if __name__ == "__main__":
    sys.exit(main())
