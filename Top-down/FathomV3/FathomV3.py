# Importing the required packages
import sys
from common import *
from damageFunctions import mortality_factor, damage_factor_builtup, damage_factor_agri
from runAnalysis import run_analysis

# Defining the main function
def main():
    # Defining the initial parameters
    country         = 'MYS'			  # ISO3166-a2 code
    haz_cat         = 'COASTAL_UNDEFENDED' 			  # Hazard type:'FLUVIAL_UNDEFENDED'; 'FLUVIAL_DEFENDED', 'PLUVIAL_DEFENDED'; 'COASTAL_UNDEFENDED'; 'COASTAL_DEFENDED'
    period          = '2050'			  # Period of the analysis: '2020', '2030', '2050', '2080'
    scenario        = 'SSP3_7.0'		  # Climate scenario: 'SSP1_2.6', 'SSP2_4.5', 'SSP3_7.0', 'SSP5_8.5'
    return_periods  = [5, 10, 20, 50, 100, 200, 500, 1000]  # example for Fathom  [5, 10, 20, 50, 100, 200, 500, 1000]
    exp_cat_list    = ['POP', 'BU']	  # ['POP', 'BU', 'AGR']
    exp_nam_list    = ['POP', 'BU']	  # if None, the default applies: 'Population':'POP', 'Built-up':'BU', 'Agricultural land':'AGR' - If not None, expect a list of same length of exp_cat_list
    adm             = 'ADM2' 			  #['ADM1', 'ADM2', 'ADM3']
    analysis_app    = 'Function'		  #['Classes', 'Function']
    min_haz_slider  = 0.1			  # Data to be ignored below threshold
    class_edges        = [0.05, 0.25, 0.50, 1.00, 2.00] # FL [0.05, 0.25, 0.50, 1.00, 2.00]
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
        run_analysis(country, haz_cat, period, scenario, return_periods, min_haz_slider,
                       exp_cat, exp_nam, adm, analysis_app, class_edges, save_check_raster)

    print("--- %s seconds ---" % (time.time() - start_time))

if __name__ == "__main__":
    sys.exit(main())
