# STATUS

- Code has been tested and is working on Linux and Windows (create dedicated enviroment). Not tested on Mac.
- This version has some small changes with respect to the previous one:
-   i) Cores is now automatic, using all available cores for the first zonal_stats and then using 1 core per RP analysis (in case there are more RPs then available cores, it will use all cores and serialize the analysis accordingly).
-   ii) Split the RPs computation into Exposure/Impact and EAE/EAI computation, the later becoming a stand-alone function
-   iii) Computes now the EAE/EAI using 3 different formulation, a) Lower Bound LB; b) Upper Bound UB, and; c) Mean of the two
-   iv) Removed the RP_EAI columns for better presentation of the results

# SETUP
We strongly recommend using the mamba package manager.

## Using MAMBA

Environment creation:

```bash
$ mamba create -n ccdr-tools --file Top-down/notebooks/win_env.yml
```

Updating the environment spec (e.g., if package version changed or a package is added/removed):

```bash
$ mamba list -n ccdr-tools --explicit > win_env.yml
```

Updating the environment (e.g., after code updates)

```bash
$ mamba update -n ccdr-tools --file Top-down/notebooks/win_env.yml
```

## Using CONDA

Environment creation:

```bash
$ conda create -name ccdr-tools --file Top-down/notebooks/win_env.yml
```

Updating the environment (e.g., after code updates)

```bash
$ conda update -name ccdr-tools --file Top-down/notebooks/win_env.yml
```

# SCRIPT OVERVIEW

- `common.py` setup the script libraries and specifies data directories
- `damageFunctions.py` includes the impact models (mathematical relationship between hazard intensity and relative damage over exposure category)
- `main.py` specifies the parameters of the analysis to run (country, hazards, return periods, classes, etc)
- `runAnalysis.py` is used to run the program according to parameters set in `main.py`

## Input data

Input data layers must be named and placed according to rules.

- Create a working directory and set it as DATA_DIR in `common.py`.
  Inside the workdir, the data folders must follow this structure:
```
    DATA_DIR/ADM: Administrative boundaries as '.gpkg' (multiple levels)
    DATA_DIR/HZD: Hazard layers as '.tif' using CRS 4326
    DATA_DIR/EXP: Exposure layers as '.tif' using CRS 4326
```
- To name datasets, use `[ISO3166_a3](https://en.wikipedia.org/wiki/ISO_3166-1_alpha-3)` country code followed by specific data identifier - which is not fixed, you need to edit it in `runAnalysis.py`.
```
    CCDR_tools/ADM/SEN_ADM.gpkg
    CCDR_tools/HZD/SEN_FL_RP10.tif
    CCDR_tools/EXP/SEN_POP.tif
```
- Read more about data formatting in the [documentation](https://gfdrr.github.io/CCDR-tools/docs/tool-setup.html).

## Setting parameters

Edit the `main.py` file to specify:
- country (`country_dd`):
- hazard type (`haz_cat_dd`): 'FL' for floods; 'HS' for heat stress; 'DR' for drought; 'LS' for landslide
- return periods (`return_periods`): list of return period scenarios as in the data, e.g. [5, 10, 20, 50, 75, 100, 200, 250, 500, 1000]
- exposure categories (`exp_cat_dd_list`): list of exposure categories: ['pop', 'builtup', 'agri']
  - exposure categories file name (`exp_cat_dd_list`): list  of same length of `exp_cat_dd_list` with file names for exposure categories: ['WPOP20', 'WSF19', 'ESA20_agri']
    If 'None', the default ['WPOP20', 'WSF19', 'ESA20_agri'] applies. 
- analysis approach (`analysis_app_dd`): ['Classes', 'Function']
  - If 'Function', you can set minimum hazard threshold value (`min_haz_slider`). Hazard value below this threshold will be ignored.
  - If 'Classes',  you can set the number and value of thresholds to consider to split hazard intensity values into bins (classes).
- admin level (`adm_dd`): specify which boundary level to use for results summary
- save check (`save_check_raster`): specify if you want to export intermediate rasters (increases processing time).

Example of `main.py` running flood analysis (`haz_cat_dd`) over Cambodia (`country_dd`) for 10 return periods (`return_periods`) over three exposure categories (`exp_cat_dd_list`) using hazard classes according to thresholds (`class_edges`); results summarised at ADM3 level (`adm_dd`). Do not save intermediate rasters (`save_check_raster`).
```
    # Defining the initial parameters
    country_dd         = 'KHM'
    haz_cat_dd         = 'FL'
    return_periods     = [5, 10, 20, 50, 75, 100, 200, 250, 500, 1000]
    min_haz_slider     = 0.05 							# FL 0.05 # TC 25.0 # ASI 0.01
    exp_cat_dd_list    = ['pop', 'builtup', 'agri']
    exp_nam_dd_list    = ['WPOP20', 'WSF19', 'ESA20_agri']
    adm_dd             = 'ADM3' 						#['ADM1', 'ADM2', 'ADM3']
    analysis_app_dd    = 'Classes' 						#['Classes', 'Function']
    class_edges        = [0.05, 0.25, 0.50, 1.00, 2.00] 			# FL [0.05, 0.25, 0.50, 1.00, 2.00] # TC [17.0, 32.0, 42.0, 49.0, 58.0, 70.0] # DR_ASI [0.01, 0.10, 0.25, 0.40, 0.55, 0.70, 0.85]
    save_check_raster  = False
```