# FATHOM v3 - FLOOD EXPOSURE AND RISK PROCESSING

This script runs on Fathom v3 scenarios in combination with population, exposure and land cover maps to produce Expeceted Annual Exposure (EAE) or Expected Annual Impact (EAI). Please check https://gfdrr.github.io/CCDR-tools for more details on the approach.



# STATUS
  - The number of processors used (nCores) is selected automatically, using all available cores for the first zonal_stats and then using 1 core per RP analysis (in case there are more RPs then available cores, it will use all cores and serialize the analysis accordingly).
  - Split the RPs computation into Exposure/Impact and EAE/EAI computation, the later becoming a stand-alone function
  - Computes now the EAE/EAI using 3 different formulation, a) Lower Bound LB; b) Upper Bound UB, and; c) Mean of the two
  - Removed the RP_EAI columns for better presentation of the results

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
- `damageFunctions.py` includes the impact models (mathematical relationship between hazard intensity and relative damage/impact over exposure category)
- `main.py` specifies the parameters of the analysis to run (country, hazards, return periods, classes, etc)
- `runAnalysis.py` the main function that is used to run the program according to parameters set in `main.py`

## Input data

Input data layers must be named and placed according to some rules, as follows:

- Create a working directory and set it as DATA_DIR (e.g. ./data) in `common.py`.
  Inside the workdir, the data folders must follow this structure:

```
    DATA_DIR/ADM: Administrative boundaries as '.gpkg' (multiple levels)
    DATA_DIR/HZD: Hazard layers as '.tif' using CRS 4326
    DATA_DIR/EXP: Exposure layers as '.tif' using CRS 4326
```
- To name datasets, use [`ISO3166_a2`](https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2) country code followed by specific data identifier - which is not fixed, you need to edit it in `runAnalysis.py`.

```
    CCDR_tools/ADM/PK_ADM.gpkg
    CCDR_tools/HZD/FL/PK_FL_RP10.tif
    CCDR_tools/EXP/PK_POP.tif
```
- Read more about data formatting in the [documentation](https://gfdrr.github.io/CCDR-tools/docs/tool-setup.html).

## Setting parameters

Edit the `main.py` file to specify:
- **country (`country`)**: [`ISO3166_a2`](https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2) country code
- **hazard type (`haz_cat`)**: `'FL'` for river floods; `'PL'` for pluvial floods; `'CF'` for coastal floods; 
- **return periods (`return_periods`)**: list of return period scenarios as in the data, e.g. `[5, 10, 20, 50, 75, 100, 200, 250, 500, 1000]`
- **exposure categories (`exp_cat_list`)**: list of exposure categories: `['POP', 'BU', 'AGR']`
  - exposure categories file name (`exp_cat_list`): list  of same length of `exp_cat_list` with file names for exposure categories, e.g.: `['GHS', 'WSF19', 'ESA20']`
    If 'None', the default `['POP', 'BU', 'AGR']` applies
- **analysis approach (`analysis_app`)**: `['Classes', 'Function']`
  - If `'Function'`, you can set minimum hazard threshold value (`min_haz_slider`). Hazard value below this threshold will be ignored
  - If `'Classes'`,  you can set the number and value of thresholds to consider to split hazard intensity values into bins (`class_edges`)
- **admin level (`adm`)**: specify which boundary level to use for results summary (must exist in the `ISOa3`_ADM.gpkg file)
- **save check (`save_check_raster`)**: specify if you want to export intermediate rasters (increases processing time) `[True, False]`

Example of `main.py` running flood analysis (`haz_cat`) over Cambodia (`country`) for 10 return periods (`return_periods`) over three exposure categories (`exp_cat_list`) using hazard classes according to thresholds (`class_edges`); results summarised at ADM3 level (`adm`). Do not save intermediate rasters (`save_check_raster`).

```
    # Defining the initial parameters - Example for function analysis
    country            = 'PK'
    haz_cat            = 'FL'
    return_periods     = [5, 10, 20, 50, 75, 100, 200, 250, 500, 1000]
    min_haz_slider     = 0.05
    exp_cat_list       = ['POP', 'BU', 'AGR']
    exp_nam_list       = ['GHS', 'WSF19', 'ESA20']
    adm                = 'ADM3'
    analysis_app       = 'Function'
    # class_edges        = [0.05, 0.25, 0.50, 1.00, 2.00]
    save_check_raster  = False
```

```
    # Defining the initial parameters - Example for class analysis
    country            = 'KH'
    haz_cat            = 'FL'
    return_periods     = [5, 10, 20, 50, 75, 100, 200, 250, 500, 1000]
    # min_haz_slider     = 0.05
    exp_cat_list       = ['POP', 'BU', 'AGR']
    exp_nam_list       = ['POP', 'BU', 'AGR']
    adm                = 'ADM3'
    analysis_app       = 'Classes'
    class_edges        = [0.05, 0.25, 0.50, 1.00, 2.00]
    save_check_raster  = False
```


## Running the analysis

```bash
$ python FathomV3.py
```

The analysis runs on all selected exposed categories, in sequence. Depending on the number of cores, the size and resolution of the data, and power of CPU, the analysis can take from less than a minute to few minutes.
E.g. for Bangladesh on a  i9-12900KF (16 cores), 64 Gb RAM: below 100 seconds.
