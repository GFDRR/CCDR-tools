# STATUS

- Code has been tested and is working on Linux and Windows (create dedicated enviroment). Not tested on Mac but most likely working as well.
- This version has some small changes with respect to the previous one, listed below:
  - The number of processors used (nCores) is now selected automatic, using all available cores for the first zonal_stats and then using 1 core per RP analysis (in case there are more RPs then available cores, it will use all cores and serialize the analysis accordingly).
  - Split the RPs computation into Exposure/Impact and EAE/EAI computation, the later becoming a stand-alone function
  - Computes now the EAE/EAI using 3 different formulation, a) Lower Bound LB; b) Upper Bound UB, and; c) Mean of the two
  - Removed the RP_EAI columns for better presentation of the results

# SETUP
We strongly recommend using the mamba or conda package manager.

## Using MAMBA (WINDOWS)

Environment creation:
```bash
$ mamba create -n CCDR-tools --file Top-down/parallelization/win_env.yml
```
Updating the environment spec (e.g., if package version changed or a package is added/removed):
```bash
$ mamba list -n CCDR-tools --explicit > win_env.yml
```
Updating the environment (e.g., after code updates)
```bash
$ mamba update -n CCDR-tools --file Top-down/parallelization/win_env.yml
```

## Using MAMBA (LINUX)

Environment creation:
```bash
$ mamba create -n CCDR-tools --file Top-down/parallelization/linux_env.yml
```
Updating the environment spec:
```bash
$ mamba list -n CCDR-tools --explicit > linux_env.yml
```
Updating the environment (e.g., after code updates)
```bash
$ mamba update -n CCDR-tools --file Top-down/parallelization/linux_env.yml
```

## Using CONDA (WINDOWS)

Environment creation:
```bash
$ conda create -name CCDR-tools --file Top-down/parallelization/win_env.yml
```
Updating the environment (e.g., after code updates)
```bash
$ conda update -name CCDR-tools --file Top-down/parallelization/win_env.yml
```

## Using CONDA (LINUX)

Environment creation:
```bash
$ conda create -name CCDR-tools --file Top-down/parallelization/linux_env.yml
```
Updating the environment (e.g., after code updates)
```bash
$ conda update -name CCDR-tools --file Top-down/parallelization/linux_env.yml
```
-------------
Activate the environment
```bash
$ activate CCDR-tools
```

# SCRIPT OVERVIEW

- `.env` specifies the directories where data are stored
- `common.py` setup the script libraries and specifies data directories
- `damageFunctions.py` includes the impact models (mathematical relationship between hazard intensity and relative damage/impact over exposure category)
- `main.py` specifies the parameters of the analysis to run (country, hazards, return periods, classes, etc)
- `runAnalysis.py` the main function that is used to run the program according to parameters set in `main.py`

## Working directory

Edit the `.env` file to specify the data folder (DATA_DIR).
You don't need to change the cache and output directory.

```
# Environment variables for the CCDR Hazard analysis notebooks

# Specify working directory, location of data files
# Use absolute paths, and keep the trailing slash
DATA_DIR = C:/Work/data

# Location to store downloaded rasters and other data
# for the analysis notebooks
CACHE_DIR = ${DATA_DIR}/cache
OUTPUT_DIR = ${DATA_DIR}/output

```

## Input data

Input data layers must be named and placed according to some rules, as follows:

- Inside the workdir, the data folders must follow this structure:
  ```
    DATA_DIR/ADM: Administrative boundaries as '.gpkg' (multiple levels)
    DATA_DIR/HZD: Hazard layers as '.tif' using CRS 4326
    DATA_DIR/EXP: Exposure layers as '.tif' using CRS 4326
  ```
- Datasets naming requires to specify [`{ISO3166_a3}`](https://en.wikipedia.org/wiki/ISO_3166-1_alpha-3) country code followed by specific data identifier. 
  ```
    DATA_DIR/ADM: {ISO}_ADM.gpkg		E.g. SEN_ADM.gpkg
    DATA_DIR/HZD: {ISO}_{HZD}_RP{n}.tif		E.g. SEN_FL_RP100.tif
    DATA_DIR/EXP: {ISO}_{EXP}.gpkg		E.g. SEN_POP.tif
  ```
  Allowed exposure categories are:
  - **`ISO`_POP.tif**: Population, as from [Global Human Settlement Layer](https://ghsl.jrc.ec.europa.eu/download.php?ds=pop) or [Worldpop](https://hub.worldpop.org/geodata/listing?id=79). Value representing population count per cell.
  - **`ISO`_BU.tif**: Built-up from [Global Human Settlement Layer](https://ghsl.jrc.ec.europa.eu/download.php?ds=bu) or [World Settlement Footprint](https://download.geoservice.dlr.de/WSF2019/). Value as density (0-1) per cell.
  - **`ISO`_AGR.tif**: Agriculture from land cover map, [ESA land cover](https://esa-worldcover.org/en) or equivalent. Value as density (0-1) per cell.

- Read more about data formatting in the [documentation](https://gfdrr.github.io/CCDR-tools/docs/tool-setup.html).

## Setting parameters

Edit the `main.py` file to specify:
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

Example of `main.py` running flood analysis (`haz_cat`) over Cambodia (`country`) for 10 return periods (`return_periods`) over three exposure categories (`exp_cat_list`) using hazard classes according to thresholds (`class_edges`); results summarised at ADM3 level (`adm`). Do not save intermediate rasters (`save_check_raster`).

```
    # Defining the initial parameters - Example for function analysis
    country            = 'KHM'
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
    country            = 'KHM'
    haz_cat            = 'FL'
    return_periods     = [5, 10, 20, 50, 75, 100, 200, 250, 500, 1000]
    # min_haz_slider     = 0.05
    exp_cat_list       = ['POP', 'BU', 'AGR']
    exp_nam_list       = ['GHS', 'WSF19', 'ESA20']
    adm                = 'ADM3'
    analysis_app       = 'Classes'
    class_edges        = [0.05, 0.25, 0.50, 1.00, 2.00]
    save_check_raster  = False
```


## Running the analysis

```bash
$ python main.py
```

The analysis runs on all selected exposed categories, in sequence. Depending on the number of cores, the size and resolution of the data, and power of CPU, the analysis can take from less than a minute to few minutes.
E.g. for Bangladesh on a  i9-12900KF (16 cores), 64 Gb RAM: below 100 seconds.
