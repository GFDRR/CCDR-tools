# Tools setup

The analytical scripts can be downloaded as:

- [**Jupyter notebooks**](https://github.com/GFDRR/CCDR-tools/tree/main/Top-down/notebooks): user-friendly script that run via browser interface.
Read more about [**Jupyter Notebooks**](https://jupyter-notebook.readthedocs.io/en/stable/notebook.html).
- [**Python code**](https://github.com/GFDRR/CCDR-tools/tree/main/Top-down/parallelization): give the user more control, and has overall better performances making use of parallel processing.

These can be downloaded and exectuted on any windows or linux machine. 
In both cases, the script expects input data to be provided according to some rules.

### Expected directories and input format

The script expects input data folders to be structured as:

```
Work dir/
 - Hazard.ipynb
 - common.py
 - Data/
   - ADM	Administrative unit layer for each country
   - HZD	Hazard layers
   - EXP	Exposure layers - Population (count), Built-up (ratio or binary), Agriculture (ratio or binary)
   - RSK	Output directory
```

- **ADMINISTRATIVE** boundaries are provided as geopackage files named as `ISO`_ADM.gpkg (e.g. `NPL`_ADM.gpkg) made of multiple layers represening different administrative boundary levels.

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

Each ADM layer should include relative ADMi_CODE and ADMi_NAME across levels to facilitate the summary of results:

  - **ADM0**

  | ISO3166_a2 | ISO3166_a3 | ADM0_CODE | ADM0_NAME | 
  |---|---|---|---|
  | String(2) | String(3) | Integer | String (20) |
 
  - **ADM1**

  | ADM0_CODE | ADM0_NAME | ADM1_CODE | ADM1_NAME | 
  |---|---|---|---|
  | Integer | String (20) | Integer | String(20) |

  - **ADM2**

  | ADM0_CODE | ADM0_NAME | ADM1_CODE | ADM1_NAME | ADM2_CODE | ADM2_NAME | 
  |---|---|---|---|---|---|
  | Integer | String (20) | Integer | String(20) | Integer | String(20) |

  - **ADM3**
  
  | ADM0_CODE | ADM0_NAME | ADM1_CODE | ADM1_NAME | ADM2_CODE | ADM2_NAME | ADM3_CODE | ADM3_NAME | 
  |---|---|---|---|---|---|---|---|
  | Integer | String (20) | Integer | String(20) | Integer | String(20) | Integer | String(20) |

- **HAZARD** layers are expected as raster files (`.tif`) named as `ISO`_`HZD`_RPi.tif (exampe for Nepal flood, RP100: `NPL_FL_RP100.tif`). Any resolution should work, but using resolution below 90m over large countries could cause very long processing and memory cap issues.

- **EXPOSURE** are expected as raster files (`.tif`) named as `ISO`_`EXP`.tif. The same suggestion about resolution applies here.

	- Population from GHSL, 90 m: `ISO`_POP.tif
	- Built-up from World Settlement Footprint or equivalent, 90 m: `ISO`_BU.tif
	- Agriculture from land cover map, ESA land cover or equivalent, 90 m: `ISO`_AGR.tif

```{caution}
When resampling exposure layers to a lower resolution, it is **strongly recommended** to align the resampled grid to exactly match the hazard grid, or viceversa.
```

<img width=600 src="https://user-images.githubusercontent.com/44863827/157419284-64e16285-6284-45ba-bc9c-01eab713c2f1.png">

```{caution}
All spatial data must use the same CRS, suggested: `EPSG 4326` (WGS 84)
```

<hr>

## Environment and libraries
- The script requires python3 - conda or mamba are encouraged
- Create a new environment named CCDR based on win_env.yml o linux_env.yml depending on your operating system.
  In Anaconda cmd prompt:

	`conda create --name CCDR --file <dir/win_env.yml>`
	
	`activate CCDR`

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

- Navigate to your working directory: `cd <Your work directory>`
  ```{figure} images/cmd_prompt.png
  ---
  align: center
  ---
  Example of Anaconda cmd prompt
  ```
- Run `jupyter notebook`. The interface should pop up in your browser.
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

### Run the analysis

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



