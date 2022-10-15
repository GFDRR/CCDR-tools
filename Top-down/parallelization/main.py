# Importing the required packages
import sys
from common import *
from damageFunctions import damage_factor_builtup, damage_factor_agri, mortality_factor
from runAnalysis import run_analysis


# Defining the main function
def main():
    # Defining the initial parameters
    country_dd         = "PNG"
    haz_cat_dd         = "FL" #'FL' for floods; 'HS' for heat stress; 'DR' for drought; 'LS' for landslide
    return_periods     = [5, 10, 20, 50, 75, 100, 200, 250, 500, 1000] # add here as will
    min_haz_slider     = 0.05
    exp_cat_dd_list    = ["pop"] #, "builtup", "agri"] #[("Population", "pop"), ("Built-up", "builtup"), ("Agriculture", "agri")]
    adm_dd             = 'ADM3' #['ADM1', 'ADM2', 'ADM3']
    time_horizon_dd    = None #[2040, 2060, 2080, 2100] - not used
    rcp_scenario_dd    = None #["2.6", "4.5", "8.5"] - not used
    analysis_app_dd    = "Function" #["Classes", "Function"]
    class_edges        = [0.05, 0.25, 0.50, 1.00, 2.00]
    save_check_raster  = False

    import time
    start_time = time.time()

    # For every exp_cat_dd
    for exp_cat_dd in exp_cat_dd_list:
        # Running the analysis
        run_analysis(country_dd, haz_cat_dd, return_periods, min_haz_slider,
                       exp_cat_dd, adm_dd, time_horizon_dd, rcp_scenario_dd, 
                       analysis_app_dd, class_edges, save_check_raster)

    print("--- %s seconds ---" % (time.time() - start_time))

if __name__ == "__main__":
    sys.exit(main())
