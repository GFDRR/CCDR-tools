# RDL-CCDR RISK ANALYTICS

The program runs in jupyter notebook. Launch GUI.ipynb and follow instructions.

The analysis runs on all selected exposed categories, in sequence, and save results as geopackage and csv. Also plots preview of results and charts.

The processing can take from less than a minute to a few minutes, sepending on the size of the country, computer power, and number of options selected. 
E.g. for Flood analysis in Bangladesh on a  i9-12900KF (16 cores), 64 Gb RAM, 3 exposure categories: below 100 seconds.

# SETUP
We strongly recommend using the mamba package manager, but conda should work too.

Environment creation:

```bash
$ mamba create -n rdl-tools --file rdl-tools.yml
```
or
```bash
$ conda create -name rdl-tools --file rdl-tools.yml
```

# SCRIPT OVERVIEW

## Input data

Default input data are sourced by the program. Custom layers can be used, just place those as follows:

- Create a working directory and set it as DATA_DIR (e.g. ./data) editing `common.py`.
  Inside the workdir, the data folders must follow this structure:

```
    DATA_DIR/HZD: Hazard layers as '.tif' using CRS 4326
    DATA_DIR/EXP: Exposure layers as '.tif' using CRS 4326
```
- To name datasets, use ISO_A3 country code followed by specific data identifier (default applies). Examples: 

```
    DATA_DIR/HZD/SEN/FLUVIAL_UNDEFENDED/2020/1in20.tif
    DATA_DIR/EXP/SEN_POP.tif
```
- Read more about data formatting in the [documentation](https://gfdrr.github.io/CCDR-tools/docs/tool-setup.html).

## Running the analysis

Activate the environment, point to your work directory, run jupyter notebook and start the [GUI](GUI.ipynb).
```bash
$ activate rdl-tools
$ cd path/to/work_directory
$ jupyter notebook 
```
Follow GUI instructions to run the analysis.
Check preview results to generate map output and output charts.

<img width="594" alt="fqwf" src="https://github.com/user-attachments/assets/41f8d337-6b61-4392-b96b-8138d56c2df5">


### Manual run
You can also use manual_run.py to run the program without jupyter notebook. Example for Flood analysis.

Edit the `manual_run.py` file to specify:
- **country (`country`)**: [`ISO3166_a3`](https://en.wikipedia.org/wiki/ISO_3166-1_alpha-3) country code
- **flood hazard type (`haz_cat`)**: `'FLUVIAL_UNDEFENDED'`,`'FLUVIAL_DEFENDED'`, `'PLUVIAL_DEFENDED'`, `'COASTAL_UNDEFENDED'`,`'COASTAL_DEFENDED'`, 
- **return periods (`return_periods`)**: list of return period scenarios as in the data, e.g. `[5, 10, 20, 50, 75, 100, 200, 250, 500, 1000]`
- **exposure categories (`exp_cat_list`)**: list of exposure categories: `['POP', 'BU', 'AGR']`
  - exposure categories file name (`exp_cat_list`): list  of same length of `exp_cat_list` with file names for exposure categories, e.g.: `['GHS', 'WSF19', 'ESA20']`
    If 'None', the default `['POP', 'BU', 'AGR']` applies
- **analysis approach (`analysis_app`)**: `['Classes', 'Function']`
  - If `'Function'`, you can set minimum hazard threshold value (`min_haz_slider`). Hazard value below this threshold will be ignored
  - If `'Classes'`,  you can set the number and value of thresholds to consider to split hazard intensity values into bins (`class_edges`)
- **admin level (`adm`)**: specify which boundary level to use for results summary (must exist in the `ISOa3`_ADM.gpkg file)
- **save check (`save_check_raster`)**: specify if you want to export intermediate rasters (greatly increases processing time) `[True, False]`

Example of `manual_run.py` running flood analysis (`haz_cat`) over Cambodia (`country`) for 10 return periods (`return_periods`) over three exposure categories (`exp_cat_list`) using hazard classes according to thresholds (`class_edges`); results summarised at ADM3 level (`adm`). Do not save intermediate rasters (`save_check_raster`).

```
    # Defining the initial parameters - Example for function analysis
    country            = 'KHM'
    haz_cat            = 'FLUVIAL_UNDEFENDED'
    return_periods     = [5, 10, 20, 50, 75, 100, 200, 250, 500, 1000]
    min_haz_slider     = 20
    exp_cat_list       = ['POP', 'BU', 'AGR']
    exp_nam_list       = ['GHS', 'WSF19', 'ESA20']
    adm                = 'ADM3'
    analysis_app       = 'Function'
    # class_edges        = []
    save_check_raster  = False
```

```
    # Defining the initial parameters - Example for class analysis
    country            = 'KHM'
    haz_cat            = 'COASTAL_DEFENDED'
    return_periods     = [5, 10, 20, 50, 75, 100, 200, 250, 500, 1000]
    # min_haz_slider     = 20
    exp_cat_list       = ['POP', 'BU', 'AGR']
    exp_nam_list       = ['GHS', 'WSF19', 'ESA20']
    adm                = 'ADM3'
    analysis_app       = 'Classes'
    class_edges        = [50, 100, 150, 200, 250]
    save_check_raster  = False
```


After saving the file, to run the analysis:

```bash
$ python manual_run.py
```
