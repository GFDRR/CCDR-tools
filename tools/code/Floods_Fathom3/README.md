# STATUS

- Code has been tested and is working on Linux and Windows (create dedicated enviroment). Not tested on Mac but most likely working as well.
- The number of processors used (nCores) is selected automatically, using all available cores for the first zonal_stats and then using 1 core per RP analysis (in case there are more RPs then available cores, it will use all cores and serialize the analysis accordingly).
- ADM units are fetched automatically from the WB ArcGIS repository (GAD).
- Population is fetched automatically from Worldpop - US constrained for the specified year. A different source can be specified by filename (without .tif extension).
- World region is fetched from country code to select appropriate damage function.

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
- `try.py` specifies the parameters of the analysis to run (country, hazards, return periods, classes, etc)
- `runAnalysis.py` the main function that is used to run the program according to parameters set in `try.py`

## Input data

Input data layers must be named and placed according to some rules, as follows:

- Create a working directory and set it as DATA_DIR (e.g. ./data) in `common.py`.
  Inside the workdir, the data folders must follow this structure:

```
    DATA_DIR/HZD: Hazard layers as '.tif' using CRS 4326
    DATA_DIR/EXP: Exposure layers as '.tif' using CRS 4326
```
- To name datasets, use ISO_A3 country code followed by specific data identifier (default applies).

```
    CCDR_tools/HZD/SEN_FL_RP10.tif
    CCDR_tools/EXP/SEN_POP.tif
```
- Read more about data formatting in the [documentation](https://gfdrr.github.io/CCDR-tools/docs/tool-setup.html).

## Setting parameters

Edit the `try.py` file to specify:
- **country (`country`)**: [`ISO3166_a3`](https://en.wikipedia.org/wiki/ISO_3166-1_alpha-3) country code
- **hazard type (`haz_cat`)**: `'FL'` for floods; `'HS'` for heat stress; `'DR'` for drought; `'LS'` for landslide
- **return periods (`return_periods`)**: list of return period scenarios as in the data, e.g. `[5, 10, 20, 50, 75, 100, 200, 250, 500, 1000]`
- **exposure categories (`exp_cat_list`)**: list of exposure categories: `['POP', 'BU', 'AGR']`
  - exposure categories file name (`exp_cat_list`): list  of same length of `exp_cat_list` with file names for exposure categories, e.g.: `['GHS', 'WSF19', 'ESA20']`
    If 'None', the default `['POP', 'BU', 'AGR']` applies
- **analysis approach (`analysis_app`)**: `['Classes', 'Function']`
  - If `'Function'`, you can set minimum hazard threshold value (`min_haz_slider`). Hazard value below this threshold will be ignored
  - If `'Classes'`,  you can set the number and value of thresholds to consider to split hazard intensity values into bins (`class_edges`)
- **admin level (`adm`)**: specify which boundary level to use for results summary (must exist in the `ISOa3`_ADM.gpkg file)
- **save check (`save_check_raster`)**: specify if you want to export intermediate rasters (increases processing time) `[True, False]`

Example of `try.py` running river flood (undefended) analysis (`haz_cat`) over Cambodia (`country`) for 10 return periods (`return_periods`) calculated for baseline (2020) over three exposure categories (`exp_cat_list`) using impact function; results summarised at ADM3 level (`adm_level`). Do not save intermediate rasters (`save_check_raster`).

```
    # Defining the initial parameters
    country         = 'KHM'						  # ISO3166-a3 code
    haz_cat         = 'FLUVIAL_UNDEFENDED' 				  # Hazard type:'FLUVIAL_UNDEFENDED'; 'FLUVIAL_DEFENDED', 'PLUVIAL_DEFENDED'; 'COASTAL_UNDEFENDED'; 'COASTAL_DEFENDED'
    period          = '2020'						  # Period of the analysis: '2020', '2030', '2050', '2080'
    scenario        = 'SSP3_7.0'					  # Climate scenario: 'SSP1_2.6', 'SSP2_4.5', 'SSP3_7.0', 'SSP5_8.5'. Empty '' if period = 2020.
    return_periods  = [5, 10, 20, 50, 75, 100, 200, 250, 500, 1000]	  # example for Fathom  [5, 10, 20, 50, 100, 200, 500, 1000]
    exp_cat_list    = ['POP', 'BU', 'AGR']	  			  # ['POP', 'BU', 'AGR']
    exp_nam_list    = ['GHS_P', 'WSF19', 'ESA20']			  # Naming of population file. If None, the default applies, Population:'POP', Built-up:'BU', Agricultural land:'AGR'.
    exp_year        = ''						  # Specifies the reference time of the WorldPOP population data (always constrained type)
                                               				  # If not None, expect a list of same length of exp_cat_list e.g. ['Tunisia_GHSL_pop_2020'].
    adm_level       = 3 						  # [1, 2, 3] depending on source availability for each country
    analysis_app    = 'Function'					  # ['Classes', 'Function']
    min_haz_slider  = 10			 			  # Data to be ignored below threshold
    class_edges        = []			 			  # Floods (cm) [5, 25, 50, 100, 200]
    save_check_raster  = False
    n_cores	       = None						  # If None, max available applies. This can overload ram genereting errors. If it happens, try reducing the number of cores.
```

Example of `try.py` running coastal flood (undefended) analysis (`haz_cat`) over Tunisia (`country`) for 10 return periods (`return_periods`) calculated for projected `period` and `scenario` (2050, SSP3-7.0), over two exposure categories (`exp_cat_list`), provided by user (`exp_nam_list`) using classes approach and specified thresholds; results summarised at ADM2 level (`adm_level`). Do not save intermediate rasters (`save_check_raster`).

```
    # Defining the initial parameters
    country         = 'TUN'						  # ISO3166-a3 code
    haz_cat         = 'COASTAL_UNDEFENDED' 				  # Hazard type:'FLUVIAL_UNDEFENDED'; 'FLUVIAL_DEFENDED', 'PLUVIAL_DEFENDED'; 'COASTAL_UNDEFENDED'; 'COASTAL_DEFENDED'
    period          = '2050'						  # Period of the analysis: '2020', '2030', '2050', '2080'
    scenario        = 'SSP3_7.0'					  # Climate scenario: 'SSP1_2.6', 'SSP2_4.5', 'SSP3_7.0', 'SSP5_8.5'. Empty '' if period = 2020.
    return_periods  = [5, 10, 20, 50, 75, 100, 200, 250, 500, 1000]	  # example for Fathom  [5, 10, 20, 50, 100, 200, 500, 1000]
    exp_cat_list    = ['POP', 'BU', 'AGR']	  			  # ['POP', 'BU', 'AGR']
    exp_nam_list    = None		 				  # Naming of population file. If None, the default applies, Population:'POP', Built-up:'BU', Agricultural land:'AGR'.
    exp_year        = ''						  # Specifies the reference time of the WorldPOP population data (always constrained type)
                                               				  # If not None, expect a list of same length of exp_cat_list e.g. ['Tunisia_GHSL_pop_2020'].
    adm_level       = 2 						  # [1, 2, 3] depending on source availability for each country
    analysis_app    = 'Classes'					 	  # ['Classes', 'Function']
    min_haz_slider  = 10			 			  # Data to be ignored below threshold
    class_edges        = [5, 25, 50, 100, 200]			 	  # Floods (cm) [5, 25, 50, 100, 200]
    save_check_raster  = False
    n_cores	       = None						  # If None, max available applies. This can overload ram genereting errors. If it happens, try reducing the number of cores.

```


## Running the analysis

```bash
$ python try.py
```

The analysis runs on all selected exposed categories, in sequence. Depending on the size of the country, the number of exposure categories, the power of CPU and the number of cores used, the analysis can take from less than a minute to a few minutes.
E.g. for Bangladesh on a  i9-12900KF (16 cores), 64 Gb RAM: below 100 seconds.
