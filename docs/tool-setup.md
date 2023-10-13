# TOOLS SETUP

The analytical scripts can be downloaded as:

- [**Jupyter notebooks**](https://github.com/GFDRR/CCDR-tools/tree/main/Top-down/notebooks): user-friendly script that run via browser interface.
Read more about [**Jupyter Notebooks**](https://jupyter-notebook.readthedocs.io/en/stable/notebook.html).
- [**Python code**](https://github.com/GFDRR/CCDR-tools/tree/main/Top-down/parallelization): give the user more control, and has overall better performances making use of parallel processing.

These can be downloaded and exectuted on any windows or linux machine. 
In both cases, the script requires proper environment setup and input data to be provided according to the instructions below.

## Python environment

- Python 3 needs to be installed on your system. We suggest the latest [Anaconda](https://www.anaconda.com/download) distribution. Mamba is also encouraged.
- Create new `CCDR-tools` environment according to your operating system: win.yml or linux.yml.
  In Anaconda cmd prompt:
  ```bash
  conda create --name CCDR-tools --file <dir/win_env.yml>`
  activate CCDR-tools
  ```

## Input data management

- Download the latest version of the notebooks or the the parallel code.
- Create folder structure as:

  ```
  Work dir/
   - Hazard.ipynb		Place the notebooks and related files in the main work directory
   - common.py
   - Parallel/		Place the parallel processing script in a sub-folder
     - ...
   - Data/
     - ADM/		Administrative boundaries layer for each country
     - HZD/		Hazard layers
     - EXP/		Exposure layers
     - RSK/		Output directory
  ```

- Download **country boundaries** for multiple administrative levels (national, sub-national) sourced from [HDX](https://data.humdata.org/dataset) or [Geoboundaries](https://www.geoboundaries.org). Note that oftern there are several versions for the same country, so be sure to use the most updated from official agencies (eg. United Nations). Verify that shapes, names and codes are consistent across different levels.

  Boundaries must be provided as a geopackage files named as `ISO`_ADM.gpkg (e.g. `NPL`_ADM.gpkg) containing multiple layers, each one represening a different administrative boundary levels:

  ```
  - ISO_ADM
    - ADM0 (country)
    - ADM1 (first-level sub-national division)
    - ADM2 (second-level sub-national division)
    - ADM3 (third-level sub-national division)
    - ...
  ```

  ```{figure} images/adm_lvl.jpg
  ---
  align: center
  ---
  Example of sub-national administrative boundaries for Senegal.
  ```

  Each layer should include relative ADMi_CODE and ADMi_NAME across levels to facilitate the summary of results:

  - **ADM0** layer

  | ISO3166_a2 | ISO3166_a3 | ADM0_CODE | ADM0_NAME | 
  |---|---|---|---|
  | String(2) | String(3) | Integer | String (20) |
 
  - **ADM1** layer

  | ADM0_CODE | ADM0_NAME | ADM1_CODE | ADM1_NAME | 
  |---|---|---|---|
  | Integer | String (20) | Integer | String(20) |

  - **ADM2** layer

  | ADM0_CODE | ADM0_NAME | ADM1_CODE | ADM1_NAME | ADM2_CODE | ADM2_NAME | 
  |---|---|---|---|---|---|
  | Integer | String (20) | Integer | String(20) | Integer | String(20) |

  - **ADM3** layer
  
  | ADM0_CODE | ADM0_NAME | ADM1_CODE | ADM1_NAME | ADM2_CODE | ADM2_NAME | ADM3_CODE | ADM3_NAME | 
  |---|---|---|---|---|---|---|---|
  | Integer | String (20) | Integer | String(20) | Integer | String(20) | Integer | String(20) |

- Download probabilistic [**hazard data**](global-hazard.md), consisting of multiple RP scenarios. Each scenario is expected as a raster file (`.tif`) named as `ISO`_`HZD`_RPi.tif (exampe for Nepal flood, RP100: `NPL_FL_RP100.tif`). Any resolution should work, but using resolution below 90m over large countries could cause very long processing and memory cap issues.

- Download [**exposure data**](global-exposure.md) for population, built-up and agricolture. Layers are expected as raster files (`.tif`) named as `ISO`_`EXP`.tif.
	- **`ISO`_POP.tif**: Population, as from [Global Human Settlement Layer](https://ghsl.jrc.ec.europa.eu/download.php?ds=pop) or [Worldpop](https://hub.worldpop.org/geodata/listing?id=79). Value as number of peope per pixel.
	- **`ISO`_BU.tif**: Built-up from [Global Human Settlement Layer](https://ghsl.jrc.ec.europa.eu/download.php?ds=bu) or [World Settlement Footprint](https://download.geoservice.dlr.de/WSF2019/). Value could be binary (0/1: absence/presence per pixel) or float (0-1: density per pixel).
	- **`ISO`_AGR.tif**: Agriculture from land cover map, [ESA land cover](https://esa-worldcover.org/en) or equivalent. Value could be binary (0/1: absence/presence per pixel) or float (0-1: density per pixel).

- Move verified input data into the proper folders:
  ```
  Work dir/Data/
  - ADM/
    - ISO_ADM.gpkg
  - HZD/
    - ISO_FL_RP10.tif
    - ISO_FL_RP100.tif
    - ISO_FL_RP1000.tif
    - ...
  - EXP/
    - ISO_POP.tif
    - ISO_BU.tif
    - ISO_AGR.tif
  ```

  ```{caution}
  All spatial data must use the same CRS, suggested: `EPSG 4326` (WGS 84)
  ```
<hr>

## Settings

Edit the `.env` file inside the notebook directories to specify the working directory:

```
# Environment variables for the CCDR Climate and Disasater Risk analysis notebooks

# Fill the below with the location of data files
# Use absolute paths with forward slashes ("/"), and keep the trailing slash
DATA_DIR = C:/Work/data

# THE ENTRIES BELOW DO NOT NEED TO BE EDITED
# Location to store results of analyses
OUTPUT_DIR = ${DATA_DIR}/RSK/

# Location to store downloaded rasters and other data
# for the analysis notebooks
CACHE_DIR = ${DATA_DIR}/cache/
```

## Run Jupyter notebooks

- Be sure to activate the correct environment
  ```bash
  activate CCDR-tools
  ```
- Navigate to your working directory: `cd <Your work directory>`
  ```bash
  cd C:\Dir\Workdir\
  ```
- Run the jupyter notebook.
  ```bash
  jupyter notebook
  ```
The interface should pop up in your browser.
- You can now run the [baseline risk screening](run-baseline.md).

## Parallel processing

### Setting parameters

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

Example of `main.py` running flood analysis (`haz_cat`) over Cambodia [KHM] (`country`) for 10 return periods (`return_periods`) over three exposure categories (`exp_cat_list`) using hazard classes according to thresholds (`class_edges`); results summarised at ADM3 level (`adm`). Do not save intermediate rasters (`save_check_raster`).

Example for function analysis:
```
    # Defining the initial parameters
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

Example for class analysis:
```
    # Defining the initial parameters
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

### Run the analysis with parallel processing

```bash
$ python main.py
```

The analysis runs on all selected exposed categories, in sequence. It will print a separate message for each iteration. In case of 3 exposure caterories, it will take three iterations to get all results.

```bash
$ Running analysis...
$ Finished analysis
$ Running analysis...
$ Finished analysis
$ Running analysis...
$ Finished analysis
```

Depending on the number of cores, the size and resolution of the data, and power of CPU, the analysis can take from less than a minute to few minutes.
E.g. for Bangladesh on a  i9-12900KF (16 cores), 64 Gb RAM: below 100 seconds.



