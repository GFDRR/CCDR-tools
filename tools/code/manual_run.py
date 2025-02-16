# Importing the required packages
import sys
from runAnalysis import (
    run_analysis, create_summary_df, prepare_excel_gpkg_files,
    prepare_sheet_name, saving_excel_and_gpgk_file, prepare_and_save_summary_df
)

# Defining the main function
def main():
    # Defining the initial parameters
    country         = 'PHL'			  # ISO3166-a3 code
    haz_type        = 'FL'            # Hazard type: 'FL', 'TC'
    haz_cat         = 'FLUVIAL_UNDEFENDED' 	  # Hazard type:'FLUVIAL_UNDEFENDED'; 'FLUVIAL_DEFENDED', 'PLUVIAL_DEFENDED'; 'COASTAL_UNDEFENDED'; 'COASTAL_DEFENDED'
    period          = '2020'			  # Period of the analysis: '2020', '2030', '2050', '2080'
    scenario        = ''		  	  # Climate scenario: 'SSP1_2.6', 'SSP2_4.5', 'SSP3_7.0', 'SSP5_8.5'. Empty '' if period = 2020.
    return_periods  = [5, 10]			  # example for Fathom  [5, 10, 20, 50, 100, 200, 500, 1000]
    exp_cat_list    = ['POP', 'BU', 'AGR']	  	  # ['POP', 'BU', 'AGR']
    exp_year        = '2020'			  # Specifies the reference time of the WorldPOP population data (always constrained type)
    exp_nam_list    = ['PHL_POP', 'PHL_BU', 'PHL_AGR']	  # Naming of population file. If None, the default applies, Population:'POP', Built-up:'BU', Agricultural land:'AGR'.
                                                  # If not None, expect a list of same length of exp_cat_list e.g. ['Tunisia_GHSL_pop_2020'].
    adm_level       = 1 			  # [1, 2, 3] depending on source availability for each country
    analysis_type    = 'Function'		  # ['Classes', 'Function']
    min_haz_slider  = 10			  # Data to be ignored below threshold
    class_edges        = [50]			  # FL [5, 25, 50, 100, 200]
    save_check_raster  = False
    n_cores	       = None			  # If None, max available applies. This can overload ram genereting errors. If it happens, try reducing the number of cores.

    import time
    start_time = time.perf_counter()

    summary_dfs = []
    
    # Prepare Excel writer
    excel_file, gpkg_file = prepare_excel_gpkg_files(country, adm_level, haz_cat, period, scenario)

    # Running the analysis    
    if exp_nam_list and len(exp_nam_list) != len(exp_cat_list): sys.exit("ERROR: Parameter 'exp_nam_list' should either be 'None' or have the same length as 'exp_cat_list'")
    # For every exp_cat
    for i in range(len(exp_cat_list)):
        # Defining the list variable to pass to run_analysis
        exp_cat = exp_cat_list[i]
        exp_nam = exp_nam_list[i]
        result_df = run_analysis(country, haz_type, haz_cat, period, scenario, return_periods, min_haz_slider,
                   exp_cat, exp_nam, exp_year, adm_level, analysis_type, class_edges, save_check_raster, n_cores)

        if result_df is None:
            print("Encountered Exception! Please fix it!")
            return
        
        sheet_name = prepare_sheet_name(analysis_type, return_periods, exp_cat)
        saving_excel_and_gpgk_file(result_df, excel_file, sheet_name, gpkg_file, exp_cat)

        # Create summary DataFrame
        summary_df = create_summary_df(result_df, return_periods, exp_cat)
        summary_dfs.append(summary_df)
    
    if summary_dfs:
        prepare_and_save_summary_df(summary_dfs, exp_cat_list, excel_file)

    print("--- %s seconds ---" % (time.perf_counter() - start_time))

if __name__ == "__main__":
    sys.exit(main())