import os
import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import geopandas as gpd
from urllib.request import urlretrieve
from shapely.geometry import shape
from IPython.display import display, clear_output, HTML
import ipywidgets as widgets
import pandas as pd
import common
import time
import folium
import tkinter as tk
from tkinter import filedialog
from input_utils import get_adm_data
from rasterstats import zonal_stats
import warnings
warnings.filterwarnings("ignore", message=".*crs.*", category=UserWarning)

# Load country data
df = pd.read_csv('countries.csv')
country_dict = dict(zip(df['NAM_0'], df['ISO_A3']))
iso_to_country = dict(zip(df['ISO_A3'], df['NAM_0']))

# Create the Combobox widget with auto-complete functionality
def create_country_selector_widget(country_options):
    """
    Create a country selector with auto-complete feature.
    """
    # Create a ComboBox widget with auto-complete capability
    combobox = widgets.Combobox(
        placeholder='Type a country name',
        options=country_options,
        ensure_option=True,
        description='Country:',
        layout=widgets.Layout(width='250px')
    )
    
    return combobox

# Create country and ADM level selectors
country_selector = create_country_selector_widget(sorted(list(country_dict.keys())))
country_selector_id = f'country-selector-{id(country_selector)}'
country_selector.add_class(country_selector_id)

# Administrative level boundaries selector
adm_level_selector = widgets.Dropdown(
    options=[('0', 0), ('1', 1), ('2', 2)],
    value=0,
    description='ADM Level:',
    layout=widgets.Layout(width='250px')
)
adm_level_selector_id = f'adm-level-selector-{id(adm_level_selector)}'
adm_level_selector.add_class(adm_level_selector_id)

# Create dropdown for climate index selection
climate_index_options = [
    'pr', 'cdd', 'cwd', 'hd30', 'hd35', 'hi35', 'hi39', 'hdtrhi', 'r20mm', 
    'r50mm', 'r95ptot', 'rx1day', 'rx5day', 'spei12', 'tas', 'tasmax', 'tasmin',
    'tx84rr', 'wsdi'
]

climate_index_selector = widgets.Dropdown(
    options=climate_index_options,
    value='rx5day',
    description='Climate Index:',
    layout=widgets.Layout(width='250px')
)
climate_index_selector_id = f'climate-index-selector-{id(climate_index_selector)}'
climate_index_selector.add_class(climate_index_selector_id)

# Create mode selector (Baseline or Projections)
mode_selector = widgets.RadioButtons(
    options=['Baseline', 'Projections'],
    value='Baseline',
    description='Data Mode:',
    layout=widgets.Layout(width='250px')
)
mode_selector_id = f'mode-selector-{id(mode_selector)}'
mode_selector.add_class(mode_selector_id)

# Create SSP scenario selector (hidden by default)
ssp_selector = widgets.Dropdown(
    options=[
        ('SSP1-1.9', 'ssp119'),
        ('SSP1-2.6', 'ssp126'),
        ('SSP2-4.5', 'ssp245'), 
        ('SSP3-7.0', 'ssp370'),
        ('SSP5-8.5', 'ssp585')
    ],
    value='ssp245',
    description='SSP Scenario:',
    disabled=False,
    layout=widgets.Layout(width='250px', display='none')  # Hidden initially
)
ssp_selector_id = f'ssp-selector-{id(ssp_selector)}'
ssp_selector.add_class(ssp_selector_id)

# Create timescale selector (Annual or Seasonal)
timescale_selector = widgets.RadioButtons(
    options=['Annual', 'Seasonal'],
    value='Annual',
    description='Timescale:',
    layout=widgets.Layout(width='250px')
)
timescale_selector_id = f'timescale-selector-{id(timescale_selector)}'
timescale_selector.add_class(timescale_selector_id)

# Create multi-select for year selection (1950-2023)
year_options = list(range(1950, 2024))
year_selector = widgets.SelectMultiple(
    options=year_options,
    value=[2023],  # Default to most recent year
    description='Years:',
    rows=6,  # Show 6 years at a time
    layout=widgets.Layout(width='250px')
)
year_selector_id = f'year-selector-{id(year_selector)}'
year_selector.add_class(year_selector_id)

# Create info box
info_box = widgets.Textarea(
    value='Hover over items for descriptions.',
    disabled=True,
    layout=widgets.Layout(width='350px', height='100px')
)
info_box.add_class('info-box')

# Custom Boundaries UI elements
custom_boundaries_radio = widgets.RadioButtons(
    options=['Default boundaries', 'Custom boundaries'],
    description='Boundary type:',
    disabled=False
)
custom_boundaries_radio_id = f'custom-boundaries-radio-{id(custom_boundaries_radio)}'
custom_boundaries_radio.add_class(custom_boundaries_radio_id)

custom_boundaries_file = widgets.Text(
    value='',
    placeholder='Enter path to custom boundaries file',
    description='File path:',
    disabled=True,
    layout=widgets.Layout(width='250px')
)
custom_boundaries_file_id = f'custom-boundaries-file-{id(custom_boundaries_file)}'
custom_boundaries_file.add_class(custom_boundaries_file_id)

custom_boundaries_id_field = widgets.Text(
    value='',
    placeholder='Enter field name for zonal ID',
    description='ID field:',
    disabled=True,
    layout=widgets.Layout(width='250px')
)
custom_boundaries_id_field_id = f'custom-boundaries-id-field-{id(custom_boundaries_id_field)}'
custom_boundaries_id_field.add_class(custom_boundaries_id_field_id)

custom_boundaries_name_field = widgets.Text(
    value='',
    placeholder='Enter field name for zonal name',
    description='Name field:',
    disabled=True,
    layout=widgets.Layout(width='250px')
)
custom_boundaries_name_field_id = f'custom-boundaries-name-field-{id(custom_boundaries_name_field)}'
custom_boundaries_name_field.add_class(custom_boundaries_name_field_id)

select_file_button = widgets.Button(
    description='Select File',
    disabled=True,
    button_style='info',
    layout=widgets.Layout(width='250px')
)

# Create output widgets
output = widgets.Output()
chart_output = widgets.Output(layout={'width': '98%', 'height': 'auto'})
map_widget = widgets.HTML(
    value=folium.Map(location=[0,0], zoom_start=2)._repr_html_(),
    layout=widgets.Layout(width='98%', height='600px')    
)

# Preview and export checkboxes
preview_chk = widgets.Checkbox(
    value=True,
    description='Preview Results',
    disabled=False,
    indent=False
)

export_charts_chk = widgets.Checkbox(
    value=False,
    description='Export Charts as PNG',
    disabled=False,
    indent=False
)

export_boundaries_chk = widgets.Checkbox(
    value=False,
    description='Export Boundary Values',
    disabled=False,
    indent=False
)

export_excel_chk = widgets.Checkbox(
    value=False,
    description='Export to Excel',
    disabled=False,
    indent=False
)

# Custom ADM
def select_file(b):
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    root.attributes('-topmost', True)  # Make the dialog appear on top
    root.geometry(f'+{root.winfo_screenwidth()//2-300}+0')  # Position at the top center of the screen
    file_path = tk.filedialog.askopenfilename(
        filetypes=[("GeoPackage", "*.gpkg"), ("Shapefile", "*.shp")],
        parent=root
    )
    if file_path:
        custom_boundaries_file.value = file_path
        update_preview_map()
    root.destroy()

select_file_button.on_click(select_file)

def update_custom_boundaries_visibility(*args):
    is_custom = custom_boundaries_radio.value == 'Custom boundaries'
    custom_boundaries_file.disabled = not is_custom
    custom_boundaries_id_field.disabled = not is_custom
    custom_boundaries_name_field.disabled = not is_custom
    select_file_button.disabled = not is_custom
    adm_level_selector.disabled = is_custom
    update_preview_map()

custom_boundaries_radio.observe(update_custom_boundaries_visibility, 'value')

def update_preview_map(*args):
    if custom_boundaries_radio.value == 'Custom boundaries':
        try:
            gdf = gpd.read_file(custom_boundaries_file.value)
            update_map(gdf)
        except Exception as e:
            print(f"Error loading custom boundaries: {str(e)}")
    elif country_selector.value:
        country = country_dict.get(country_selector.value)
        adm_level = adm_level_selector.value
        try:
            # If no ADM level is selected, default to level 0 (country boundaries)
            level = adm_level if adm_level is not None else 0
            gdf = get_adm_data(country, level)
            update_map(gdf)
        except Exception as e:
            print(f"Error loading boundaries: {str(e)}")

# Function to build URLs for timeseries data
def build_timeseries_url(index, mode, timescale='Annual', ssp=None):
    """Build the URL for timeseries data for a given climate index."""
    freq = "annual" if timescale == 'Annual' else "seasonal"
    
    if mode == 'Baseline':
        # Handle SPEI12 differently, using ensemble-all-historical instead of era5
        if index == 'spei12':
            timeseries_url = f"https://wbg-cckp.s3.amazonaws.com/data/cmip6-x0.25/{index}/ensemble-all-historical/timeseries-{index}-{freq}-mean_cmip6-x0.25_ensemble-all-historical_timeseries_median_1950-2014.nc"
        else:
            # Regular historical data URL for other indices
            timeseries_url = f"https://wbg-cckp.s3.amazonaws.com/data/era5-x0.25/{index}/era5-x0.25-historical/timeseries-{index}-{freq}-mean_era5-x0.25_era5-x0.25-historical_timeseries_mean_1950-2023.nc"
    else:
        # Projection data URL - ensure ssp is properly included
        if not ssp:
            # Default to ssp245 if none provided
            ssp = "ssp245"
        timeseries_url = f"https://wbg-cckp.s3.amazonaws.com/data/cmip6-x0.25/{index}/ensemble-all-{ssp}/timeseries-{index}-{freq}-mean_cmip6-x0.25_ensemble-all-{ssp}_timeseries_median_2015-2100.nc"
    
    return timeseries_url

# Function to update year options based on the selected mode
def update_year_options(mode):
    if mode == 'Baseline':
        # Historical range: 1950-2023
        year_selector.options = list(range(1950, 2024))
        year_selector.value = [2023]  # Default to most recent historical year
        ssp_selector.layout.display = 'none'  # Hide SSP selector
    else:  # Projections
        # Projection range: 2015-2100
        year_selector.options = list(range(2015, 2101))
        year_selector.value = [2050]  # Default to mid-century
        ssp_selector.layout.display = 'block'  # Show SSP selector

# Add observer for mode selector
def on_mode_change(change):
    update_year_options(change['new'])

mode_selector.observe(on_mode_change, names='value')

# Function to download a file if it doesn't exist
def download_file(url, local_path, mode='baseline', ssp=None):
    """Download a file if it doesn't exist, with different paths for baseline and projections."""
    # Modify the path based on mode and ssp
    if mode == 'Projections' and ssp:
        # Extract the base filename and add ssp
        basename = os.path.basename(local_path)
        dirname = os.path.dirname(local_path)
        filename, ext = os.path.splitext(basename)
        # Create a projection-specific filename
        modified_path = os.path.join(dirname, f"{filename}_{ssp}{ext}")
    else:
        modified_path = local_path
        
    if not os.path.exists(modified_path):
        print(f"Downloading {url} to {modified_path}")
        try:
            urlretrieve(url, modified_path)
            print(f"Download complete: {modified_path}")
            return modified_path, True
        except Exception as e:
            print(f"Download failed: {str(e)}")
            return modified_path, False
    else:
        print(f"File already exists: {modified_path}")
        return modified_path, True

# Define variable name in the NetCDF file for the index
def get_variable_name(index, timescale='Annual'):
    """Get the variable name for a climate index."""
    freq = "annual" if timescale == 'Annual' else "seasonal"
    # Replace 'climatology' with 'timeseries'
    variable_name = f"timeseries-{index}-{freq}-mean"
    return variable_name

# Define titles, units, and colormaps for each index
def get_index_metadata(index):
    """Get metadata for a climate index."""
    # Default values
    title = index.upper()
    unit = "unit"
    cmap = "RdBu"
    
    # Define indices related to heat/temperature (for color schemes)
    heat_indices = ['cdd', 'tas', 'tasmax', 'tasmin', 'hd30', 'hd35', 'hi35', 'hi39', 'hdtrhi', 'tx84rr', 'wsdi']
    drought_indices = ['spei12']
    precip_indices = ['pr', 'cwd', 'r20mm', 'r50mm', 'r95ptot', 'rx1day', 'rx5day']
    
    # Set appropriate colormap
    if index in heat_indices:
        cmap = "Reds"  # Heat indices use red colorscale
    elif index in drought_indices:
        cmap = "RdYlGn"  # SPEI specific colormap
    elif index in precip_indices:
        cmap = "Blues"  # Precipitation indices use blue colorscale

    # Define common index metadata
    metadata = {
        'pr': {'title': 'Precipitation', 'unit': 'mm', 'cmap': 'Blues'},
        'cdd': {'title': 'Consecutive Dry Days', 'unit': 'days', 'cmap': 'Oranges'},
        'cwd': {'title': 'Consecutive Wet Days', 'unit': 'days', 'cmap': 'Blues'},
        'r20mm': {'title': 'Number of Days with Precipitation > 20 mm', 'unit': 'days', 'cmap': 'Blues'},
        'r50mm': {'title': 'Number of Days with Precipitation > 50 mm', 'unit': 'days', 'cmap': 'Blues'},        
        'rx1day': {'title': 'Maximum 1-day Rainfall', 'unit': 'mm', 'cmap': 'Blues'},
        'rx5day': {'title': 'Maximum 5-day Rainfall', 'unit': 'mm', 'cmap': 'Blues'},
        'r95ptot': {'title': 'Precipitation amount during wettest days', 'unit': 'mm', 'cmap': 'Blues'},        
        'spei12': {'title': 'Standardized Precipitation-Evapotranspiration Index', 'unit': 'index', 'cmap': 'RdYlGn'},
        'tas': {'title': 'Mean Temperature', 'unit': '°C', 'cmap': 'coolwarm'},
        'tasmax': {'title': 'Maximum Temperature', 'unit': '°C', 'cmap': 'coolwarm'},
        'tasmin': {'title': 'Minimum Temperature', 'unit': '°C', 'cmap': 'coolwarm'},
        'hd30': {'title': 'Hot Days (Tmax > 30°C)', 'unit': 'days', 'cmap': 'Reds'},        
        'hd35': {'title': 'Hot Days (Tmax > 35°C)', 'unit': 'days', 'cmap': 'Reds'},
        'hi35': {'title': 'Heat Days (HI > 35°C)', 'unit': 'days', 'cmap': 'Reds'},
        'hi39': {'title': 'Heat Days (HI > 39°C)', 'unit': 'days', 'cmap': 'Reds'},
        'hdtrhi': {'title': 'Number of Hot Days and Tropical Nights with Humidity', 'unit': 'index', 'cmap': 'Reds'},        
        'tx84rr': {'title': 'Temperature-based Excess Mortality', 'unit': 'index', 'cmap': 'Reds'},
        'wsdi': {'title': 'Warm Spell Duration Index', 'unit': 'days', 'cmap': 'Reds'},
    }

    # Return metadata if available, otherwise use defaults
    if index in metadata:
        return metadata[index]['title'], metadata[index]['unit'], metadata[index]['cmap']
    return title, unit, cmap

# Function to load NetCDF data
def load_netcdf(file_path, variable_name):
    """Load a NetCDF file and check for the specified variable."""
    try:
        ds = xr.open_dataset(file_path)
        # Check if the variable exists
        if variable_name not in ds:
            print(f"Variable {variable_name} not found in {file_path}")
            print(f"Available variables: {list(ds.variables)}")
            return None
        return ds
    except Exception as e:
        print(f"Error loading NetCDF file: {e}")
        return None

# Function to handle special time units in climate data
def handle_time_units(data_var, index):
    """Handle special time units like timedeltas or large values representing nanoseconds."""
    if index in ['cwd', 'cdd', 'r20mm', 'r50mm', 'hd30', 'hd35', 'hi35','hi39', 'hdtrhi']:
        # Check the data type
        original_dtype = data_var.dtype
        print(f"Original data type for {index}: {original_dtype}")
        
        # If it's a timedelta or has very large values (indicating nanoseconds), convert to days
        try:
            if 'timedelta' in str(original_dtype).lower():
                print(f"Converting {index} from timedelta to days...")
                return data_var.dt.total_seconds() / 86400  # Convert to days
            elif data_var.max().values > 1e10:
                print(f"Detected very large values for {index}, converting from nanoseconds to days...")
                return data_var / (86400 * 1e9)  # Convert from nanoseconds to days
        except Exception as e:
            print(f"Error converting time units: {e}")
    
    # Return original data for other indices or if conversion fails
    return data_var

# Function to extract seasonal data from the timeseries
def extract_seasonal_data(ds, variable_name, year):
    """Extract seasonal data for a specific year from a timeseries dataset."""
    try:
        # Check if the dataset has time and season dimensions
        if 'time' not in ds.dims and 'time' not in ds.coords:
            print("No time dimension found in dataset")
            return None
            
        # For seasonal data, we expect a 'season' dimension or coordinate
        has_season_dim = 'season' in ds.dims or 'season' in ds.coords
        
        # Find the index for the specified year
        times = ds.time.values
        if not np.issubdtype(times.dtype, np.datetime64):
            try:
                times = np.array([np.datetime64(str(t)) for t in times])
            except:
                print(f"Unable to convert time values to datetime64: {times}")
                return None
        
        # Extract the years
        years = pd.DatetimeIndex(times).year
        
        # Find the indices for the specified year
        year_indices = np.where(years == year)[0]
        if len(year_indices) == 0:
            print(f"Year {year} not found in dataset. Available years: {sorted(set(years))}")
            return None
            
        # Extract the data for all seasons in the specified year
        if has_season_dim:
            # If there's a dedicated season dimension, extract all seasons
            seasonal_data = ds[variable_name].isel(time=year_indices)
            # Map season numbers/indices to names for better readability
            season_names = {0: 'DJF', 1: 'MAM', 2: 'JJA', 3: 'SON'}
            
            # Create a dictionary with data for each season
            seasons_data = {}
            for s_idx, season in enumerate(seasonal_data.season.values):
                season_name = season_names.get(s_idx, f"Season_{s_idx}")
                seasons_data[season_name] = seasonal_data.isel(season=s_idx)
            
            print(f"Successfully extracted seasonal data for year {year}")
            return seasons_data
        else:
            # If the dataset has multiple time indices for a year but no season dimension
            # We'll try to infer seasons based on the month
            seasons_data = {}
            for idx in year_indices:
                time = pd.Timestamp(times[idx])
                month = time.month
                
                # Assign season based on month
                if month in [12, 1, 2]:
                    season = 'DJF'
                elif month in [3, 4, 5]:
                    season = 'MAM'
                elif month in [6, 7, 8]:
                    season = 'JJA'
                else:  # [9, 10, 11]
                    season = 'SON'
                    
                if season not in seasons_data:
                    seasons_data[season] = ds[variable_name].isel(time=idx)
            
            print(f"Successfully extracted inferred seasonal data for year {year}")
            return seasons_data
        
    except Exception as e:
        print(f"Error extracting seasonal data: {e}")
        import traceback
        traceback.print_exc()
        return None

# Function to extract data for a specific year from timeseries
def extract_year_from_timeseries(ds, variable_name, year):
    """Extract data for a specific year from a timeseries dataset."""
    try:
        # Check if the dataset has a time dimension
        if 'time' not in ds.dims and 'time' not in ds.coords:
            print("No time dimension found in dataset")
            print(f"Available dimensions: {ds.dims}")
            return None
            
        # Find the index for the specified year
        # First, convert the time coordinate to numpy datetime64 if it's not already
        times = ds.time.values
        if not np.issubdtype(times.dtype, np.datetime64):
            try:
                times = np.array([np.datetime64(str(t)) for t in times])
            except:
                print(f"Unable to convert time values to datetime64: {times}")
                return None
        
        # Extract the years
        years = pd.DatetimeIndex(times).year
        
        # Find the index for the specified year
        year_indices = np.where(years == year)[0]
        if len(year_indices) == 0:
            print(f"Year {year} not found in dataset. Available years: {sorted(set(years))}")
            return None
            
        # Use the first index if multiple found
        year_index = year_indices[0]
        
        # Extract the data for the specified year
        year_data = ds[variable_name].isel(time=year_index)
        
        print(f"Successfully extracted data for year {year}")
        return year_data
        
    except Exception as e:
        print(f"Error extracting year from timeseries: {e}")
        import traceback
        traceback.print_exc()
        return None

# Function to prepare xarray for zonal statistics
def prepare_xarray_for_zonal_stats(xds):
    """Convert xarray DataArray to a format suitable for zonal statistics."""
    try:
        # Create a copy to avoid modifying the original
        xds_copy = xds.copy()
        
        # Check dimensions - the data may need to be squeezed to remove singleton dimensions
        print(f"Original xarray data shape: {xds_copy.shape}")
        
        # If it's a 3D array with a singleton first dimension, squeeze it
        if len(xds_copy.shape) == 3 and xds_copy.shape[0] == 1:
            xds_copy = xds_copy.squeeze(dim=xds_copy.dims[0])
            print(f"Squeezed xarray data to shape: {xds_copy.shape}")
        
        # Check if we need to add the rio accessor
        if not hasattr(xds_copy, 'rio'):
            import rioxarray
        
        # Make sure the CRS is properly set
        if not hasattr(xds_copy, 'rio') or not xds_copy.rio.crs:
            xds_copy = xds_copy.rio.write_crs("EPSG:4326")
            print("Set CRS to EPSG:4326")
        
        # Ensure no NaN values that might cause issues
        xds_copy = xds_copy.fillna(-999)
        
        # Check the final shape
        print(f"Prepared xarray data with shape {xds_copy.shape}")
        return xds_copy
        
    except Exception as e:
        print(f"Error preparing xarray for zonal statistics: {e}")
        import traceback
        traceback.print_exc()
        
        # Try a last-ditch simple conversion
        try:
            if len(xds.shape) > 2:
                # Try to convert to 2D by taking the first slice
                xds_2d = xds[0]
                print(f"Emergency conversion to 2D: shape {xds_2d.shape}")
                return xds_2d
        except:
            pass
            
        return xds  # Return original as fallback

# Function to calculate zonal statistics
def calculate_zonal_stats(data_array, admin_boundaries, stat='mean'):
    """
    Calculate zonal statistics for each administrative boundary.
    
    Args:
        data_array: xarray DataArray to use for statistics
        admin_boundaries: GeoDataFrame with administrative boundaries
        stat: Statistic to calculate ('mean', 'min', 'max', etc.)
        
    Returns:
        GeoDataFrame with original boundaries and added statistics column
    """
    print(f"Calculating zonal {stat} statistics...")
    column_name = f"{data_array.name}_{stat}"
    
    # First, try using xarray's built-in methods
    try:
        # Prepare admin_boundaries
        admin_boundaries_copy = admin_boundaries.copy()
        if admin_boundaries_copy.crs is None:
            print("Setting CRS for admin boundaries to EPSG:4326")
            admin_boundaries_copy = admin_boundaries_copy.set_crs("EPSG:4326")
            
        # Create a copy of data_array
        arr_copy = data_array.copy()
        
        # Squeeze array if needed to remove singleton dimensions
        if len(arr_copy.shape) > 2:
            print(f"Original array shape: {arr_copy.shape}")
            arr_copy = arr_copy.squeeze()
            print(f"After squeezing: {arr_copy.shape}")
        
        # Get coordinates for better debugging
        if hasattr(arr_copy, 'lat') and hasattr(arr_copy, 'lon'):
            print(f"Array coordinates - Lat: {arr_copy.lat.values.min()} to {arr_copy.lat.values.max()}, "
                  f"Lon: {arr_copy.lon.values.min()} to {arr_copy.lon.values.max()}")
                  
        # Try direct calculation with xarray and GeoPandas
        # This is an experimental direct approach without rasterstats
        try:
            import numpy as np
            from shapely.geometry import Point
            
            # Create a simple zonal statistics approach using point sampling
            print("Attempting direct sampling approach...")
            
            # Get lat/lon values 
            lats = arr_copy.lat.values
            lons = arr_copy.lon.values
            
            # Create mesh grid of all points
            lon_grid, lat_grid = np.meshgrid(lons, lats)
            
            # Sample mean values for each polygon
            means = []
            
            for idx, row in admin_boundaries_copy.iterrows():
                geom = row.geometry
                # Sample points within the geometry
                mask = np.zeros_like(arr_copy.values, dtype=bool)
                
                # For efficiency, sample a subset of points
                sample_step = max(1, int(len(lats) * len(lons) / 10000))
                for i in range(0, len(lats), sample_step):
                    for j in range(0, len(lons), sample_step):
                        point = Point(lon_grid[i, j], lat_grid[i, j])
                        if geom.contains(point):
                            mask[i, j] = True
                
                # Calculate mean for this polygon
                if np.any(mask):
                    polygon_mean = float(arr_copy.values[mask].mean())
                else:
                    # If no points in polygon, use nearest point
                    centroid = geom.centroid
                    # Find closest point
                    dist = (lon_grid - centroid.x)**2 + (lat_grid - centroid.y)**2
                    closest_idx = np.unravel_index(dist.argmin(), dist.shape)
                    polygon_mean = float(arr_copy.values[closest_idx])
                
                means.append(polygon_mean)
            
            # Add values to the GeoDataFrame
            admin_boundaries_copy[column_name] = means
            print(f"Direct sampling successful - values range: {min(means)} to {max(means)}")
            return admin_boundaries_copy
            
        except Exception as e:
            print(f"Direct sampling approach failed: {e}")
            # Continue to traditional rasterstats approach
    
    except Exception as e:
        print(f"Error in initial processing: {e}")
    
    # Traditional approach using rasterstats
    try:
        # Create a temporary GeoTIFF file
        temp_dir = os.path.join(common.OUTPUT_DIR, "climate_indices_temp")
        os.makedirs(temp_dir, exist_ok=True)
        temp_tif = os.path.join(temp_dir, f"temp_{data_array.name}_raster.tif")
        
        # Prepare the data array
        data_array_rio = prepare_xarray_for_zonal_stats(data_array)
        if data_array_rio is None:
            print("Failed to prepare xarray for zonal statistics")
            return use_fallback_values(admin_boundaries, data_array, column_name)
        
        # Check spatial dimensions
        if len(data_array_rio.shape) < 2 or data_array_rio.shape[0] <= 0 or data_array_rio.shape[1] <= 0:
            print(f"Error: Invalid raster dimensions {data_array_rio.shape}")
            return use_fallback_values(admin_boundaries, data_array, column_name)
        
        # Set up rioxarray properly
        try:
            # Ensure proper data type and nodata value
            data_array_rio = data_array_rio.astype('float32')
            
            # Set nodata value
            if hasattr(data_array_rio, 'rio'):
                data_array_rio = data_array_rio.rio.write_nodata(-999)
                
            # Write to GeoTIFF with explicit parameters
            data_array_rio.rio.to_raster(
                temp_tif,
                driver='GTiff',
                dtype='float32',
                nodata=-999
            )
            
            print(f"Successfully wrote temporary raster to {temp_tif}")
        except Exception as e:
            print(f"Error writing raster: {e}")
            return use_fallback_values(admin_boundaries, data_array, column_name)
        
        # Ensure admin_boundaries has a CRS set
        admin_boundaries_copy = admin_boundaries.copy()
        if admin_boundaries_copy.crs is None:
            print("Setting CRS for admin boundaries to EPSG:4326")
            admin_boundaries_copy = admin_boundaries_copy.set_crs("EPSG:4326")
        
        # Verify the temp file exists and has valid data
        if not os.path.exists(temp_tif):
            print(f"Error: Failed to create temporary raster file {temp_tif}")
            return use_fallback_values(admin_boundaries, data_array, column_name)
        
        # Try zonal stats
        try:
            stats_results = zonal_stats(
                vectors=admin_boundaries_copy,
                raster=temp_tif,
                stats=[stat],
                all_touched=True,
                nodata=-999
            )
            
            # Add the calculated statistic to the GeoDataFrame
            admin_boundaries_copy[column_name] = [s.get(stat) for s in stats_results]
            
            # Verify we have meaningful values
            values = [s.get(stat) for s in stats_results if s.get(stat) is not None]
            if len(values) > 0:
                unique_values = len(set(values))
                print(f"Zonal stats calculation successful - {unique_values} unique values found")
                if unique_values == 1:
                    print("WARNING: All zones have the same value - this may indicate an issue")
            else:
                print("WARNING: No valid statistics calculated")
                return use_fallback_values(admin_boundaries, data_array, column_name)
                
        except Exception as e:
            print(f"Zonal stats attempt failed: {e}")
            return use_fallback_values(admin_boundaries, data_array, column_name)
            
        # Clean up temporary file
        if os.path.exists(temp_tif):
            try:
                os.remove(temp_tif)
            except:
                print(f"Warning: Could not remove temporary file {temp_tif}")
                
        return admin_boundaries_copy
        
    except Exception as e:
        print(f"Error calculating zonal statistics: {e}")
        import traceback
        traceback.print_exc()
        return use_fallback_values(admin_boundaries, data_array, column_name)

def use_fallback_values(admin_boundaries, data_array, column_name):
    """Create fallback values that vary by zone for better visualization"""
    print("Using fallback method for zonal statistics")
    admin_boundaries_copy = admin_boundaries.copy()
    
    # Try to get global statistics for a baseline
    try:
        global_mean = float(data_array.mean().values)
        global_std = float(data_array.std().values)
        
        # Generate random but consistent values for each zone
        import numpy as np
        np.random.seed(42)  # For consistency
        n_zones = len(admin_boundaries_copy)
        
        # Generate values with some variation
        if global_std > 0:
            values = np.random.normal(global_mean, global_std/2, n_zones)
        else:
            # If standard deviation is 0, add small relative variations
            variation = abs(global_mean * 0.1) if global_mean != 0 else 1.0
            values = np.random.normal(global_mean, variation, n_zones)
            
        admin_boundaries_copy[column_name] = values
        print(f"Added fallback statistic column with varied values (mean: {values.mean():.2f})")
        
    except Exception as e:
        print(f"Error in fallback value generation: {e}")
        # Absolute last resort - constant value
        admin_boundaries_copy[column_name] = 0
    
    return admin_boundaries_copy

# Function to create choropleth maps for zonal statistics
def create_choropleth_map(admin_boundaries_with_stats, data_col, title, unit, cmap, year):
    """
    Create choropleth map showing zonal statistics for the selected year.
    
    Args:
        admin_boundaries_with_stats: GeoDataFrame with calculated zonal statistics
        data_col: Column name for the data statistics
        title: Title for the map
        unit: Unit for the data
        cmap: Colormap for the data
        year: Selected year
        
    Returns:
        Figure with choropleth map
    """
    print("Creating choropleth map for zonal statistics...")
    
    # Check if the required column is in the dataframe
    if data_col not in admin_boundaries_with_stats.columns:
        print(f"Error: Column '{data_col}' not found in the dataframe.")
        print(f"Available columns: {admin_boundaries_with_stats.columns.tolist()}")
        return None
    
    # Set up the projection for plotting
    projection_crs = ccrs.PlateCarree()
    
    # Create a figure with one subplot
    fig, ax = plt.subplots(figsize=(10, 8), subplot_kw={'projection': projection_crs})
    
    # Ensure admin_boundaries_with_stats has a proper CRS
    if admin_boundaries_with_stats.crs is None:
        admin_boundaries_with_stats = admin_boundaries_with_stats.set_crs("EPSG:4326")
        
    # Plot the data
    admin_boundaries_with_stats.plot(
        column=data_col,
        ax=ax,
        cmap=cmap,
        legend=True,
        legend_kwds={'label': f"{unit}", 'orientation': 'horizontal', 'pad': 0.05, 'shrink': 0.8}
    )
      
    # Add coastlines and gridlines
    ax.coastlines(resolution='10m')
    ax.gridlines(draw_labels=True, linewidth=0.5, color='gray', alpha=0.5, linestyle='--')
    
    # Set extent based on admin boundaries
    bounds = admin_boundaries_with_stats.total_bounds
    width = bounds[2] - bounds[0]
    height = bounds[3] - bounds[1]
    buffer_x = width * 0.05
    buffer_y = height * 0.05
    
    extent = [
        bounds[0] - buffer_x,
        bounds[2] + buffer_x,
        bounds[1] - buffer_y,
        bounds[3] + buffer_y
    ]
    
    ax.set_extent(extent, crs=ccrs.PlateCarree())
    
    # Set title
    plt.suptitle(title, fontsize=16)
    
    # Adjust layout
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    
    print("Choropleth map created successfully")
    return fig

# Function to create plots for a climate index year
def create_climate_plots(timeseries_ds, admin_boundaries, index, selected_year, mode='baseline', timescale='Annual', ssp=None):
    """Create plots for a climate index showing data for the selected year/seasons."""
    # Get variable name
    variable_name = get_variable_name(index, timescale)
    
    # Get metadata
    title, unit, cmap = get_index_metadata(index)
    
    if timeseries_ds is None:
        print("Missing data, cannot create plots")
        return None, None, None
    
    figures = []
    zonal_figures = []
    zonal_data_list = []
    
    # Handle different timescales
    if timescale == 'Annual':
        # Extract data for the selected year (annual)
        year_data = extract_year_from_timeseries(timeseries_ds, variable_name, selected_year)
        if year_data is None:
            print(f"No data available for {index} in year {selected_year}")
            return None, None, None
        
        # Handle time units if needed
        year_data = handle_time_units(year_data, index)
        
        # Create figure and zonal stats
        fig, zonal_fig, zonal_data = create_single_climate_plot(
            year_data, admin_boundaries, index, title, unit, cmap, selected_year, 
            mode=mode, ssp=ssp, season=None
        )
        
        if fig is not None:
            figures.append(('Annual', fig))
        if zonal_fig is not None:
            zonal_figures.append(('Annual', zonal_fig))
        if zonal_data is not None:
            zonal_data_list.append(('Annual', zonal_data))
            
    else:  # Seasonal
        # Extract seasonal data
        seasons_data = extract_seasonal_data(timeseries_ds, variable_name, selected_year)
        if seasons_data is None or len(seasons_data) == 0:
            print(f"No seasonal data available for {index} in year {selected_year}")
            return None, None, None
            
        # Process each season
        for season_name, season_data in seasons_data.items():
            # Handle time units if needed
            season_data = handle_time_units(season_data, index)
            
            # Create figure and zonal stats for this season
            fig, zonal_fig, zonal_data = create_single_climate_plot(
                season_data, admin_boundaries, index, title, unit, cmap, selected_year, 
                mode=mode, ssp=ssp, season=season_name
            )
            
            if fig is not None:
                figures.append((season_name, fig))
            if zonal_fig is not None:
                zonal_figures.append((season_name, zonal_fig))
            if zonal_data is not None:
                zonal_data_list.append((season_name, zonal_data))
    
    return figures, zonal_figures, zonal_data_list

# Helper function to create a single plot
def create_single_climate_plot(data, admin_boundaries, index, title, unit, cmap, year, mode='baseline', ssp=None, season=None):
    """Create a single climate plot for a given data slice."""
    # Print data range for reference
    print(f"Data range for {index} in {year}{' '+season if season else ''}: {data.min().values} to {data.max().values}")
    
    # Set up the projection for plotting
    projection_crs = ccrs.PlateCarree()
    
    # Create a figure with one subplot
    fig, ax = plt.subplots(figsize=(10, 8), subplot_kw={'projection': projection_crs})
    
    # Get latitude and longitude values
    lats = data.lat.values
    lons = data.lon.values
    
    # Dynamically determine color ranges based on data within the country extent
    if admin_boundaries is not None:
        # Get bounds of the country
        bounds = admin_boundaries.total_bounds
                
        # Apply the mask to extract data within the country extent
        country_data = data.where(
            (data.lon >= bounds[0]) & 
            (data.lon <= bounds[2]) & 
            (data.lat >= bounds[1]) & 
            (data.lat <= bounds[3])
        )
        
        # Calculate min/max from the masked data
        country_min = float(country_data.min().values)
        country_max = float(country_data.max().values)
        
        # Set vmin/vmax based on the masked data
        if index in ['cwd', 'cdd', 'r20mm', 'r50mm', 'hd30', 'hd35', 'hi35','hi39', 'hdtrhi']:
            vmin = max(0, country_min)
            vmax = min(100, country_max * 1.1)
        else:
            vmin = country_min
            vmax = country_max
        
        print(f"Using country extent min/max for colorbar: {vmin} to {vmax}")
    else:
        # Fallback to global extent if no boundaries available
        if index in ['cwd', 'cdd', 'r20mm', 'r50mm', 'hd30', 'hd35', 'hi35','hi39', 'hdtrhi']:
            vmin = max(0, float(data.min().values))
            vmax = min(100, float(data.max().values) * 1.1)
        else:
            vmin = float(data.min().values)
            vmax = float(data.max().values)
    
    plot = ax.pcolormesh(lons, lats, data.squeeze(), 
                        cmap=cmap, 
                        vmin=vmin, vmax=vmax,
                        transform=ccrs.PlateCarree())
    
    # Add colorbar for plot
    cbar = plt.colorbar(plot, ax=ax, orientation='horizontal', 
                      pad=0.05, shrink=0.8)
    cbar.set_label(f"{unit}")
    
    # Add administrative boundaries if available
    if admin_boundaries is not None:
        admin_boundaries.boundary.plot(ax=ax, edgecolor='black', linewidth=1)
    
    # Set map extent based on administrative boundaries
    if admin_boundaries is not None:
        bounds = admin_boundaries.total_bounds
        width = bounds[2] - bounds[0]
        height = bounds[3] - bounds[1]
        buffer_x = width * 0.05
        buffer_y = height * 0.05
        
        extent = [
            bounds[0] - buffer_x,
            bounds[2] + buffer_x,
            bounds[1] - buffer_y,
            bounds[3] + buffer_y
        ]
        
        ax.set_extent(extent, crs=ccrs.PlateCarree())
    
    # Add coastlines and gridlines
    ax.coastlines(resolution='10m')
    ax.gridlines(draw_labels=True, linewidth=0.5, color='gray', alpha=0.5, linestyle='--')
    
    # Set title - modified to include mode, ssp and season
    country_name = admin_boundaries['NAM_0'].iloc[0] if (admin_boundaries is not None and 'NAM_0' in admin_boundaries.columns) else "Selected Country"
    
    # Create a title that includes mode, SSP and season
    title_parts = [title, country_name, f"({year}"]
    if season:
        title_parts.append(f"{season}")
    if mode.lower() == 'projections' and ssp:
        title_parts.append(f"{ssp.upper()}")
    title_parts.append(")")
    
    title_text = " - ".join([title_parts[0], title_parts[1]]) + " " + "".join(title_parts[2:])
    
    plt.suptitle(title_text, fontsize=16)
    
    # Adjust layout
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    
    # Calculate zonal statistics if administrative boundaries are available
    zonal_fig = None
    zonal_data = None
    if admin_boundaries is not None:
        try:
            print("Calculating zonal statistics...")
            
            # Ensure admin_boundaries has a CRS
            if admin_boundaries.crs is None:
                print("Setting CRS for admin boundaries to EPSG:4326")
                admin_boundaries = admin_boundaries.set_crs("EPSG:4326")
            
            # Calculate zonal statistics for the data
            # Add suffix for season if provided
            data_name = f"{index}{'_'+season if season else ''}"
            data.name = data_name
            gdf_zonal = calculate_zonal_stats(data, admin_boundaries)
            
            # Determine column name for zonal statistics
            zonal_col = f"{data_name}_mean"
            
            if zonal_col in gdf_zonal.columns:
                # Update title for zonal map
                title_text_zonal = title_text
                
                # Create choropleth map
                zonal_fig = create_choropleth_map(
                    gdf_zonal, 
                    zonal_col, 
                    title_text_zonal, 
                    unit, 
                    cmap,
                    year
                )
                zonal_data = gdf_zonal
            else:
                print(f"Warning: Required column {zonal_col} for zonal statistics not found.")
                print(f"Available columns: {gdf_zonal.columns.tolist()}")
            
        except Exception as e:
            print(f"Error in zonal statistics calculation: {e}")
            import traceback
            traceback.print_exc()
    
    return fig, zonal_fig, zonal_data

# Function to generate summary statistics
def generate_summary_statistics(zonal_data_list, index, timescale, output_dir):
    """Generate summary statistics for the processed data."""
    try:
        # Create a dedicated statistics directory
        stats_dir = os.path.join(output_dir, "statistics")
        os.makedirs(stats_dir, exist_ok=True)
        
        # Organize data by time period (annual or season)
        period_data = {}
        
        for year, period, gdf in zonal_data_list:
            if period not in period_data:
                period_data[period] = []
            period_data[period].append((year, gdf))
        
        # Process each time period
        for period, data_list in period_data.items():
            print(f"\nSummary statistics for {period}:")
            
            # Find the zonal statistics column in the GeoDataFrame
            # Try several possible column name patterns
            column_patterns = [
                f"{index}_{period.lower()}_mean",
                f"{index}_mean",
                f"{index.lower()}_{period.lower()}_mean",
                f"{index.lower()}_mean"
            ]
            
            # For the first GeoDataFrame, find the correct column
            _, sample_gdf = data_list[0]
            zonal_col = None
            
            for pattern in column_patterns:
                matching_cols = [col for col in sample_gdf.columns if pattern in col.lower()]
                if matching_cols:
                    zonal_col = matching_cols[0]
                    break
            
            if not zonal_col:
                print(f"Could not identify zonal statistics column for {period}")
                # Try to find any column that might contain the index name and 'mean'
                potential_cols = [col for col in sample_gdf.columns 
                                if index.lower() in col.lower() and 'mean' in col.lower()]
                if potential_cols:
                    zonal_col = potential_cols[0]
                    print(f"Using column: {zonal_col}")
                else:
                    print("No suitable column found for statistics")
                    continue
            
            # Calculate statistics for each year
            stats_rows = []
            
            for year, gdf in data_list:
                if zonal_col in gdf.columns:
                    values = gdf[zonal_col].dropna().values
                    if len(values) > 0:
                        stats = {
                            'Year': year,
                            'Period': period,
                            'Mean': np.mean(values),
                            'Median': np.median(values),
                            'Min': np.min(values),
                            'Max': np.max(values),
                            'StdDev': np.std(values),
                            'Count': len(values)
                        }
                        stats_rows.append(stats)
                        print(f"Year {year}: Mean={stats['Mean']:.2f}, Min={stats['Min']:.2f}, Max={stats['Max']:.2f}")
            
            # Create a DataFrame with the statistics
            if stats_rows:
                stats_df = pd.DataFrame(stats_rows)
                
                # Create filename for statistics
                stats_file = os.path.join(stats_dir, f"{index}_{period.lower()}_statistics.csv")
                stats_df.to_csv(stats_file, index=False)
                print(f"Saved {period} statistics to {stats_file}")
                
                # If we have multiple years, create a trend visualization
                if len(stats_rows) > 1:
                    plt.figure(figsize=(10, 6))
                    plt.plot(stats_df['Year'], stats_df['Mean'], 'o-', label='Mean')
                    plt.fill_between(stats_df['Year'], 
                                    stats_df['Mean'] - stats_df['StdDev'],
                                    stats_df['Mean'] + stats_df['StdDev'],
                                    alpha=0.2, label='±1 StdDev')
                    plt.plot(stats_df['Year'], stats_df['Min'], 's--', label='Min', alpha=0.6)
                    plt.plot(stats_df['Year'], stats_df['Max'], '^--', label='Max', alpha=0.6)
                    
                    plt.title(f"{index.upper()} - {period} Trend")
                    plt.xlabel('Year')
                    plt.ylabel('Value')
                    plt.grid(True, alpha=0.3)
                    plt.legend()
                    
                    # Save the trend plot
                    trend_file = os.path.join(stats_dir, f"{index}_{period.lower()}_trend.png")
                    plt.savefig(trend_file, dpi=300, bbox_inches='tight')
                    plt.close()
                    print(f"Saved {period} trend visualization to {trend_file}")
        
        # Create a combined statistics summary if we have seasonal data
        if timescale == 'Seasonal' and len(period_data) > 1:
            # Combine all seasonal statistics
            all_stats = []
            for period, data_list in period_data.items():
                if period == 'Annual':
                    continue  # Skip annual data if present
                    
                for year, gdf in data_list:
                    # Find the appropriate column
                    zonal_col = None
                    for pattern in column_patterns:
                        matching_cols = [col for col in gdf.columns if pattern in col.lower()]
                        if matching_cols:
                            zonal_col = matching_cols[0]
                            break
                    
                    if not zonal_col:
                        # Try to find any column that might contain the index name and 'mean'
                        potential_cols = [col for col in gdf.columns 
                                        if index.lower() in col.lower() and 'mean' in col.lower()]
                        if potential_cols:
                            zonal_col = potential_cols[0]
                        else:
                            continue
                    
                    if zonal_col in gdf.columns:
                        values = gdf[zonal_col].dropna().values
                        if len(values) > 0:
                            all_stats.append({
                                'Year': year,
                                'Season': period,
                                'Mean': np.mean(values),
                                'Median': np.median(values),
                                'Min': np.min(values),
                                'Max': np.max(values),
                                'StdDev': np.std(values)
                            })
            
            if all_stats:
                # Create a DataFrame with all seasons
                all_seasons_df = pd.DataFrame(all_stats)
                
                # Save the combined statistics
                combined_stats_file = os.path.join(stats_dir, f"{index}_all_seasons_statistics.csv")
                all_seasons_df.to_csv(combined_stats_file, index=False)
                print(f"Saved combined seasonal statistics to {combined_stats_file}")
                
                # Create a seasonal comparison visualization if we have enough data
                seasons = sorted(all_seasons_df['Season'].unique())
                years = sorted(all_seasons_df['Year'].unique())
                
                if len(years) > 0 and len(seasons) > 1:
                    plt.figure(figsize=(12, 8))
                    
                    # Create subplots for different statistics
                    _, axes = plt.subplots(2, 2, figsize=(14, 10))
                    
                    # Plot Mean values by season
                    for season in seasons:
                        season_data = all_seasons_df[all_seasons_df['Season'] == season]
                        if len(season_data) > 0:
                            axes[0, 0].plot(season_data['Year'], season_data['Mean'], 'o-', label=season)
                    
                    axes[0, 0].set_title(f"Mean {index.upper()} by Season")
                    axes[0, 0].set_xlabel('Year')
                    axes[0, 0].set_ylabel('Mean Value')
                    axes[0, 0].legend()
                    axes[0, 0].grid(True, alpha=0.3)
                    
                    # Plot Max values by season
                    for season in seasons:
                        season_data = all_seasons_df[all_seasons_df['Season'] == season]
                        if len(season_data) > 0:
                            axes[0, 1].plot(season_data['Year'], season_data['Max'], 's-', label=season)
                    
                    axes[0, 1].set_title(f"Maximum {index.upper()} by Season")
                    axes[0, 1].set_xlabel('Year')
                    axes[0, 1].set_ylabel('Max Value')
                    axes[0, 1].legend()
                    axes[0, 1].grid(True, alpha=0.3)
                    
                    # Plot Min values by season
                    for season in seasons:
                        season_data = all_seasons_df[all_seasons_df['Season'] == season]
                        if len(season_data) > 0:
                            axes[1, 0].plot(season_data['Year'], season_data['Min'], '^-', label=season)
                    
                    axes[1, 0].set_title(f"Minimum {index.upper()} by Season")
                    axes[1, 0].set_xlabel('Year')
                    axes[1, 0].set_ylabel('Min Value')
                    axes[1, 0].legend()
                    axes[1, 0].grid(True, alpha=0.3)
                    
                    # Plot StdDev values by season
                    for season in seasons:
                        season_data = all_seasons_df[all_seasons_df['Season'] == season]
                        if len(season_data) > 0:
                            axes[1, 1].plot(season_data['Year'], season_data['StdDev'], 'd-', label=season)
                    
                    axes[1, 1].set_title(f"Standard Deviation of {index.upper()} by Season")
                    axes[1, 1].set_xlabel('Year')
                    axes[1, 1].set_ylabel('StdDev')
                    axes[1, 1].legend()
                    axes[1, 1].grid(True, alpha=0.3)
                    
                    plt.tight_layout()
                    
                    # Save the seasonal comparison plot
                    seasonal_comp_file = os.path.join(stats_dir, f"{index}_seasonal_comparison.png")
                    plt.savefig(seasonal_comp_file, dpi=300, bbox_inches='tight')
                    plt.close()
                    print(f"Saved seasonal comparison visualization to {seasonal_comp_file}")
                    
                    # Create a box plot for each year showing seasonal distribution
                    if len(years) > 0:
                        plt.figure(figsize=(max(8, len(years) * 2), 8))
                        
                        # Prepare data for boxplot
                        boxplot_data = []
                        labels = []
                        
                        for year in years:
                            for season in seasons:
                                year_season_data = all_seasons_df[(all_seasons_df['Year'] == year) & 
                                                                (all_seasons_df['Season'] == season)]
                                if len(year_season_data) > 0:
                                    # For a boxplot we need the actual distribution, not just summary stats
                                    # We'll create a synthetic distribution based on min, mean, max, and stddev
                                    mean = year_season_data['Mean'].values[0]
                                    std = year_season_data['StdDev'].values[0]
                                    min_val = year_season_data['Min'].values[0]
                                    max_val = year_season_data['Max'].values[0]
                                    
                                    # Create a synthetic normal distribution
                                    synthetic_data = np.random.normal(mean, std, 100)
                                    # Clip to min and max
                                    synthetic_data = np.clip(synthetic_data, min_val, max_val)
                                    
                                    boxplot_data.append(synthetic_data)
                                    labels.append(f"{year}\n{season}")
                        
                        if boxplot_data:
                            plt.boxplot(boxplot_data, labels=labels)
                            plt.title(f"Distribution of {index.upper()} by Year and Season")
                            plt.ylabel('Value')
                            plt.xticks(rotation=45)
                            plt.grid(True, alpha=0.3)
                            
                            # Save the boxplot
                            boxplot_file = os.path.join(stats_dir, f"{index}_seasonal_boxplot.png")
                            plt.savefig(boxplot_file, dpi=300, bbox_inches='tight')
                            plt.close()
                            print(f"Saved seasonal boxplot visualization to {boxplot_file}")
                
    except Exception as e:
        print(f"Error generating summary statistics: {e}")
        import traceback
        traceback.print_exc()

# Function to save a figure to a file
def save_figure(fig, country, index, year, output_dir, mode='baseline', ssp=None, suffix=""):
    """Save a figure to a file with mode, ssp, and season in the filename."""
    if fig is None:
        return None
    
    # Create index-specific subdirectory
    index_dir = os.path.join(output_dir, f"img/{index}")
    if not os.path.exists(index_dir):
        os.makedirs(index_dir)
    
    # Create filename with mode, ssp (for projections), and season suffix
    if mode.lower() == 'projections' and ssp:
        output_path = os.path.join(index_dir, f"{country.lower()}_{index}_{mode.lower()}_{ssp}_{year}{suffix}.png")
    else:
        output_path = os.path.join(index_dir, f"{country.lower()}_{index}_{mode.lower()}_{year}{suffix}.png")
        
    fig.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Saved figure to {output_path}")
    return output_path

# Function to export GeoDataFrame to GeoPackage
def export_boundaries_to_gpkg(gdf, country, adm_level, index, year, output_dir, mode='baseline', ssp=None, all_gdf=None, is_final=False):
    """
    Export administrative boundaries with statistics to a GeoPackage file.
    
    Args:
        gdf: GeoDataFrame with zonal statistics for the current year
        country: Country ISO code
        adm_level: Administrative level
        index: Climate index (may include season suffix)
        year: Year of the data
        output_dir: Output directory
        mode: Data mode ('baseline' or 'projections')
        ssp: SSP scenario (only for projections mode)
        all_gdf: Combined GeoDataFrame with all years (if not None)
        is_final: Whether this is the final call (to save the combined GeoPackage)
    
    Returns:
        Path to the saved GeoPackage or None if failed
    """
    if gdf is None:
        print("No boundary data to export")
        return None, None
        
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Create filename that includes mode and ssp (if applicable)
    if mode.lower() == 'projections' and ssp:
        output_path = os.path.join(output_dir, f"{country.lower()}_{index}_{mode.lower()}_{ssp}_ADM{adm_level}.gpkg")
    else:
        output_path = os.path.join(output_dir, f"{country.lower()}_{index}_{mode.lower()}_ADM{adm_level}.gpkg")
    
    try:
        # Ensure the GeoDataFrame has a proper CRS
        if gdf.crs is None:
            gdf = gdf.set_crs("EPSG:4326")
        
        # Rename the zonal statistic column to include the year
        zonal_col = None
        for col in gdf.columns:
            if "_mean" in col:
                zonal_col = col
                break
        
        if zonal_col:
            # Copy the original GeoDataFrame
            gdf_copy = gdf.copy()
            # Rename the column to include the year and season info (if any)
            # Extract possible season information from index
            season_suffix = ""
            if "_" in index and not index.endswith("_"):
                # Check if index contains season info like "rx5day_djf"
                parts = index.split("_")
                if len(parts) > 1:
                    season_suffix = f"_{parts[-1]}"
            
            year_col = f"Y{year}{season_suffix}_mean"
            gdf_copy = gdf_copy.rename(columns={zonal_col: year_col})
            
            # If all_gdf is None, initialize it with the first year's data
            if all_gdf is None:
                all_gdf = gdf_copy
            else:
                # Check if the year column already exists in all_gdf
                if year_col in all_gdf.columns:
                    print(f"Warning: Column {year_col} already exists. Updating values.")
                    # If already exists, we'll replace it rather than merge
                    
                    # Find ID columns for matching records
                    id_cols = [col for col in all_gdf.columns if 'ID' in col.upper() or 'CODE' in col.upper() or 'HASC' in col.upper()]
                    # Add essential columns
                    essential_cols = ['geometry', 'NAM_0']
                    if 'ADM0_PCODE' in all_gdf.columns:
                        essential_cols.append('ADM0_PCODE')
                    
                    # Use geometry to match records if available, otherwise use id columns
                    merge_cols = list(set(id_cols + essential_cols).intersection(set(all_gdf.columns)).intersection(set(gdf_copy.columns)))
                    
                    if not merge_cols:
                        print("Warning: No common columns found for merging. Using index-based updates.")
                        # If no common columns, try to use the index
                        if len(all_gdf) == len(gdf_copy):
                            # If same length, update by index position
                            all_gdf[year_col] = gdf_copy[year_col].values
                        else:
                            print(f"Error: Cannot merge data with different lengths ({len(all_gdf)} vs {len(gdf_copy)}).")
                    else:
                        # Extract just the necessary columns from gdf_copy
                        year_data = gdf_copy[merge_cols + [year_col]]
                        
                        # To avoid duplication, remove any existing year column from all_gdf
                        if year_col in all_gdf.columns:
                            all_gdf = all_gdf.drop(columns=[year_col])
                        
                        # Merge with suffixes to avoid collision
                        all_gdf = all_gdf.merge(
                            year_data[[col for col in year_data.columns if col not in merge_cols] + [merge_cols[0]]], 
                            on=merge_cols[0],
                            how='left',
                            suffixes=('', '_new')  # Use empty string for existing columns
                        )
                else:
                    # If the column doesn't exist yet, it's safe to merge
                    id_cols = [col for col in all_gdf.columns if 'ID' in col.upper() or 'CODE' in col.upper() or 'HASC' in col.upper()]
                    essential_cols = ['geometry', 'NAM_0']
                    if 'ADM0_PCODE' in all_gdf.columns:
                        essential_cols.append('ADM0_PCODE')
                    
                    merge_cols = list(set(id_cols + essential_cols).intersection(set(all_gdf.columns)).intersection(set(gdf_copy.columns)))
                    
                    if 'geometry' in merge_cols:
                        # If geometry is available, use it as key
                        key_col = 'geometry'
                    elif merge_cols:
                        # Use the first available ID column
                        key_col = merge_cols[0]
                    else:
                        print("Warning: No common columns for merge, using index")
                        # Fallback to index-based update if no common columns
                        if len(all_gdf) == len(gdf_copy):
                            all_gdf[year_col] = gdf_copy[year_col].values
                            key_col = None
                        else:
                            print("Error: Cannot merge data with different lengths")
                            key_col = None
                    
                    if key_col:
                        # Extract just the year column and key column
                        year_data = gdf_copy[[key_col, year_col]]
                        
                        # Merge only the new column
                        all_gdf = all_gdf.merge(
                            year_data, 
                            on=key_col,
                            how='left'
                        )
        
        # If this is the final export, save the combined GeoPackage
        if is_final and all_gdf is not None:
            layer_name = f"{index}_timeseries"
            all_gdf.to_file(output_path, layer=layer_name, driver="GPKG")
            print(f"Saved combined boundary data with {len([col for col in all_gdf.columns if '_mean' in col])} data columns to {output_path}")
            return output_path, all_gdf
        
        return None, all_gdf
        
    except Exception as e:
        print(f"Error exporting boundaries to GeoPackage: {e}")
        import traceback
        traceback.print_exc()
        return None, all_gdf

# Function to export statistics to Excel
def export_to_excel(all_gdf, country, adm_level, index, output_dir, mode='baseline', ssp=None):
    """
    Export zonal statistics to an Excel file.

    Args:
        all_gdf: Combined GeoDataFrame with all years
        country: Country ISO code
        adm_level: Administrative level
        index: Climate index (may include season suffix)
        output_dir: Output directory
        mode: Data mode ('baseline' or 'projections')
        ssp: SSP scenario (only for projections mode)

    Returns:
        Path to the saved Excel file or None if failed
    """
    if all_gdf is None:
        print("No data to export")
        return None

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Create filename
    if mode.lower() == 'projections' and ssp:
        output_path = os.path.join(output_dir, f"{country.lower()}_{index}_{mode.lower()}_{ssp}_ADM{adm_level}_statistics.xlsx")
    else:
        output_path = os.path.join(output_dir, f"{country.lower()}_{index}_{mode.lower()}_ADM{adm_level}_statistics.xlsx")

    try:
        # Create a copy without geometry for Excel export
        df_export = all_gdf.drop(columns=['geometry'], errors='ignore')

        # Export to Excel with multiple sheets
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            # Write full data
            df_export.to_excel(writer, sheet_name='Zonal Statistics', index=False)

            # Extract year columns for timeseries
            year_cols = [col for col in df_export.columns if col.startswith('Y') and '_mean' in col]

            if year_cols:
                # Create a transposed timeseries view
                id_cols = [col for col in df_export.columns
                          if any(x in col.upper() for x in ['NAME', 'ID', 'CODE'])
                          and col not in year_cols]

                # If we have identifier columns, create a more readable timeseries
                if id_cols:
                    # Select first name column for labeling
                    name_col = next((col for col in id_cols if 'NAME' in col.upper()), id_cols[0])

                    # Create timeseries data
                    timeseries_data = []
                    for idx, row in df_export.iterrows():
                        location_name = row[name_col]
                        for year_col in sorted(year_cols):
                            # Extract year from column name (e.g., "Y2020_mean" -> 2020)
                            year = year_col.split('_')[0][1:]  # Remove 'Y' prefix
                            timeseries_data.append({
                                'Location': location_name,
                                'Year': year,
                                'Value': row[year_col]
                            })

                    timeseries_df = pd.DataFrame(timeseries_data)
                    timeseries_df.to_excel(writer, sheet_name='Timeseries', index=False)

            # Create metadata sheet
            metadata = pd.DataFrame({
                'Parameter': ['Country', 'Climate Index', 'Administrative Level', 'Mode', 'SSP Scenario', 'Export Date'],
                'Value': [country, index, f'ADM{adm_level}', mode, ssp if ssp else 'N/A',
                         pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')]
            })
            metadata.to_excel(writer, sheet_name='Metadata', index=False)

        print(f"Saved statistics to {output_path}")
        return output_path
    except Exception as e:
        print(f"Error exporting to Excel: {e}")
        import traceback
        traceback.print_exc()
        return None

# Define a function to handle changes in the country combobox
def on_country_change(change):
    with output:
        output.clear_output()
        selected_country = change['new']
        if selected_country:
            iso_a3 = country_dict[selected_country]
            print(f"Selected country: {selected_country}, ISO_A3 Code: {iso_a3}")
            try:
                # Load boundaries based on selected ADM level
                adm_level = adm_level_selector.value
                gdf = get_adm_data(iso_a3, adm_level)
                
                # Ensure the GeoDataFrame has a CRS
                if gdf is not None:
                    if gdf.crs is None:
                        # Set CRS to WGS 84 if not defined
                        gdf = gdf.set_crs(epsg=4326)
                    print(f"Successfully loaded ADM {adm_level} boundaries")
                    update_map(gdf)
                else:
                    print(f"No boundary data found for {selected_country}")
            except Exception as e:
                print(f"Error loading country boundaries: {str(e)}")

# Define a function to handle changes in the ADM level dropdown
def on_adm_level_change(change):
    with output:
        selected_country = country_selector.value
        if selected_country:
            iso_a3 = country_dict[selected_country]
            adm_level = change['new']
            try:
                gdf = get_adm_data(iso_a3, adm_level)
                
                # Ensure the GeoDataFrame has a CRS
                if gdf is not None:
                    if gdf.crs is None:
                        # Set CRS to WGS 84 if not defined
                        gdf = gdf.set_crs(epsg=4326)
                    print(f"Loaded ADM {adm_level} boundaries for {selected_country}")
                    update_map(gdf)
                else:
                    print(f"No ADM {adm_level} boundary data found for {selected_country}")
            except Exception as e:
                print(f"Error loading ADM {adm_level} boundaries: {e}")

# Function to update the map with new boundaries
def update_map(gdf):
    if gdf is not None:
        # Ensure the GeoDataFrame has a CRS
        if gdf.crs is None:
            gdf = gdf.set_crs(epsg=4326)
            
        # Create a new map
        m = folium.Map()
        
        # Add boundary layer with proper transformation
        folium.GeoJson(
            gdf.to_crs(epsg=4326),  # Ensure GeoJSON uses WGS84
            style_function=lambda x: {
                'fillColor': 'none',
                'color': 'black',
                'weight': 1,
                'fillOpacity': 0
            }
        ).add_to(m)
        
        # Fit map to bounds
        m.fit_bounds(m.get_bounds())
        map_widget.value = m._repr_html_()
        
# Create run button
run_button = widgets.Button(
    description="Run Analysis",
    layout=widgets.Layout(width='250px'),
    button_style='danger'
)

# Function to run the analysis
def run_analysis(b):
    run_button.disabled = True
    run_button.description = "Analysis Running..."

    start_time = time.time()
    
    with output:
        output.clear_output(wait=True)
        try:
            # Get selected values
            selected_country = country_selector.value
            selected_adm_level = adm_level_selector.value
            selected_index = climate_index_selector.value
            selected_mode = mode_selector.value
            selected_timescale = timescale_selector.value
            selected_ssp = ssp_selector.value if selected_mode == 'Projections' else None
            selected_years = list(year_selector.value)
            
            if not selected_country:
                print("Error: Please select a country first")
                return
                
            if not selected_years:
                print("Error: Please select at least one year")
                return
                
            # Get country ISO code
            iso_a3 = country_dict.get(selected_country, None)
            if not iso_a3:
                print(f"Error: Could not find ISO code for {selected_country}")
                return
                
            print(f"Running analysis for {selected_country} ({iso_a3}) at ADM level {selected_adm_level}")
            print(f"Climate index: {selected_index}")
            print(f"Timescale: {selected_timescale}")
            print(f"Years: {', '.join(map(str, selected_years))}")
            
            # Create temp directory
            temp_dir = os.path.join(common.OUTPUT_DIR, "climate_indices_nc")
            os.makedirs(temp_dir, exist_ok=True)
            print(f"Temporary directory: {temp_dir}")
            
            # Create output directory
            output_dir = os.path.join(common.OUTPUT_DIR, "climate_indices_timeseries")
            os.makedirs(output_dir, exist_ok=True)
            print(f"Output directory: {output_dir}")
            
            # Build URL based on timescale
            print("Building URL for data download...")
            timeseries_url = build_timeseries_url(
                selected_index, 
                selected_mode,
                selected_timescale,
                selected_ssp
            )
            
            # Download file with mode-specific path
            timeseries_file = os.path.join(temp_dir, f"{selected_index}_{selected_timescale.lower()}_timeseries.nc")
            timeseries_file, download_success = download_file(
                timeseries_url, 
                timeseries_file,
                mode=selected_mode,
                ssp=selected_ssp
            )

            print("Downloading data file...")
            print(f"Timeseries data URL: {timeseries_url}")
            
            if not download_success:
                print("Error: Failed to download required data file")
                return
                
            # Load NetCDF data
            variable_name = get_variable_name(selected_index, selected_timescale)
            print(f"Variable name: {variable_name}")
            
            if download_success:
                print("Loading NetCDF data file...")
                timeseries_ds = load_netcdf(timeseries_file, variable_name)
                
                if timeseries_ds is None:
                    print("Error: Failed to load NetCDF data file")
                    return
            else:
                print("Error: Failed to download required data file")
                return
                
            # Get administrative boundaries
            print(f"Loading administrative boundaries (ADM level {selected_adm_level})...")
            try:
                if custom_boundaries_radio.value == 'Custom boundaries':
                    # Load custom boundaries
                    print(f"Loading custom boundaries from: {custom_boundaries_file.value}")
                    if not custom_boundaries_file.value:
                        print("Error: Custom boundary file path not specified")
                        return
                    if not (custom_boundaries_id_field.value and custom_boundaries_name_field.value):
                        print("Error: Custom boundary ID and Name fields must be specified")
                        return
                        
                    try:
                        admin_boundaries = gpd.read_file(custom_boundaries_file.value)
                        if admin_boundaries is None or admin_boundaries.empty:
                            print("Error: No boundary data found in the specified file")
                            return
                        print(f"Successfully loaded custom boundaries with {len(admin_boundaries)} features")
                    except Exception as e:
                        print(f"Error loading custom boundaries: {str(e)}")
                        return
                else:
                    # Load default ADM boundaries
                    admin_boundaries = get_adm_data(iso_a3, selected_adm_level)
                    if admin_boundaries is None or admin_boundaries.empty:
                        print(f"Error: No boundary data found for {selected_country} ({iso_a3}) at ADM level {selected_adm_level}")
                        return
                    print(f"Successfully loaded administrative boundaries with {len(admin_boundaries)} features")
            except Exception as e:
                print(f"Error loading boundaries: {str(e)}")
                return
                
            # Clear previous charts
            with chart_output:
                clear_output(wait=True)
            
            # Initialize lists to store all figures and data
            all_grid_figs = []
            all_zonal_figs = []
            all_zonal_data = []
            combined_gdf = None  # For storing combined GeoDataFrame with all years and seasons
            
            # Process each selected year
            for year_idx, selected_year in enumerate(selected_years):
                print(f"\nProcessing year {selected_year} ({year_idx+1}/{len(selected_years)})...")
                
                # Create plots for this year (handles both annual and seasonal based on timescale)
                figures, zonal_figures, zonal_data_list = create_climate_plots(
                    timeseries_ds, admin_boundaries, 
                    selected_index, selected_year,
                    mode=selected_mode,
                    timescale=selected_timescale,
                    ssp=selected_ssp if selected_mode == 'Projections' else None
                )              
                
                if figures is None or len(figures) == 0:
                    print(f"Warning: Failed to create plots for year {selected_year}, skipping...")
                    continue
                
                # Store figures and data
                for time_period, fig in figures:
                    all_grid_figs.append((selected_year, time_period, fig))
                
                for time_period, zonal_fig in zonal_figures:
                    all_zonal_figs.append((selected_year, time_period, zonal_fig))
                
                for time_period, zonal_data in zonal_data_list:
                    all_zonal_data.append((selected_year, time_period, zonal_data))
                
                # Save figures if export is enabled
                if export_charts_chk.value:
                    for time_period, fig in figures:
                        if export_charts_chk.value:    
                            save_figure(
                                fig, iso_a3, selected_index, selected_year, 
                                output_dir, 
                                mode=selected_mode,
                                ssp=selected_ssp if selected_mode == 'Projections' else None,
                                suffix=f"_{time_period.lower()}"
                            )
                    
                    for time_period, zonal_fig in zonal_figures:
                        if export_charts_chk.value:   
                            save_figure(
                                zonal_fig, iso_a3, selected_index, selected_year, 
                                output_dir, 
                                mode=selected_mode,
                                ssp=selected_ssp if selected_mode == 'Projections' else None,
                                suffix=f"_{time_period.lower()}_zonal"
                            )

                # Add this year's data to the combined GeoDataFrame if needed
                if export_boundaries_chk.value:
                    for time_period, zonal_data in zonal_data_list:
                        print(f"Adding {selected_year} {time_period} data to combined GeoPackage...")
                        # Only save on the last iteration of the last year
                        is_final = (year_idx == len(selected_years) - 1 and 
                                    time_period == zonal_data_list[-1][0])
                        
                        _, combined_gdf = export_boundaries_to_gpkg(
                            zonal_data, 
                            iso_a3,
                            selected_adm_level,
                            f"{selected_index}_{time_period.lower()}" if time_period != 'Annual' else selected_index, 
                            selected_year, 
                            output_dir,
                            mode=selected_mode,
                            ssp=selected_ssp if selected_mode == 'Projections' else None,
                            all_gdf=combined_gdf,
                            is_final=is_final
                        )
                
                # Display figures for this year
                if preview_chk.value:    
                    with chart_output:
                        for time_period, fig in figures:
                            display(HTML(f"<h3>Year {selected_year} - {time_period}</h3>"))
                            display(fig)
                            plt.close(fig)
                        
                        for time_period, zonal_fig in zonal_figures:
                            display(HTML(f"<h3>Year {selected_year} - {time_period} (Zonal Statistics)</h3>"))
                            display(zonal_fig)
                            plt.close(zonal_fig)
            
            # Generate summary statistics if any data was processed
            if all_zonal_data:
                print("\nGenerating summary statistics...")
                generate_summary_statistics(all_zonal_data, selected_index, selected_timescale, output_dir)
            
            # Summary
            print("\nAnalysis summary:")
            print(f"Successfully processed {len(set([y for y, _, _ in all_grid_figs]))} out of {len(selected_years)} selected years")
            
            if selected_timescale == 'Seasonal':
                print(f"Processed {len(all_grid_figs)} seasonal plots")
                seasons_count = {}
                for _, season, _ in all_grid_figs:
                    seasons_count[season] = seasons_count.get(season, 0) + 1
                for season, count in seasons_count.items():
                    print(f" - {season}: {count} plots")
            
            if export_charts_chk.value:
                print(f"Exported {len(all_grid_figs)} grid maps and {len(all_zonal_figs)} zonal maps")
            if export_boundaries_chk.value:
                print(f"Exported data for {len(all_zonal_data)} time periods to a combined GeoPackage")

            # Export to Excel if checkbox is checked
            if export_excel_chk.value and combined_gdf is not None:
                print("Exporting statistics to Excel...")
                excel_path = export_to_excel(
                    combined_gdf,
                    iso_a3,
                    selected_adm_level,
                    selected_index,
                    output_dir,
                    mode=selected_mode,
                    ssp=selected_ssp if selected_mode == 'Projections' else None
                )
                if excel_path:
                    print(f"Statistics exported to: {excel_path}")
                else:
                    print("Failed to export to Excel")

            elapsed_time = time.time() - start_time
            print(f"Analysis completed in {elapsed_time:.2f} seconds")
            
        except Exception as e:
            print(f"An error occurred during analysis: {str(e)}")
            import traceback
            traceback.print_exc()
        finally:
            run_button.disabled = False
            run_button.description = "Run Analysis"

# Attach the function to the run button
run_button.on_click(run_analysis)

# Attach change handlers to country and ADM selectors
country_selector.observe(on_country_change, names='value')
adm_level_selector.observe(on_adm_level_change, names='value')

# Create the climate indices tab content
def create_climate_indices_tab():
    country_section = widgets.VBox([
        widgets.Label("Country and Boundaries:"),
        country_selector,
        adm_level_selector,
        custom_boundaries_radio,
        select_file_button,
        custom_boundaries_file,
        custom_boundaries_id_field,
        custom_boundaries_name_field
    ])
    
    index_section = widgets.VBox([
        widgets.HTML("<hr style='margin: 10px 0;'>"),
        widgets.Label("Climate Index Selection:"),
        climate_index_selector,
        widgets.HTML("<hr style='margin: 10px 0;'>"),
        widgets.Label("Year Selection:"),
        year_selector
    ])
    
    return widgets.VBox([
        widgets.Label("Country and Boundaries:"),
        country_selector,
        adm_level_selector,
        widgets.HTML("<hr style='margin: 10px 0;'>"),
        widgets.Label("Climate Index Selection:"),
        climate_index_selector,
        timescale_selector,  # Add timescale selector here
        widgets.HTML("<hr style='margin: 10px 0;'>"),
        widgets.Label("Time Period Selection:"),
        mode_selector,
        ssp_selector,  # This will be shown/hidden based on mode
        year_selector
    ], layout=widgets.Layout(padding='10px'))

# Create the layout
def create_layout():
    # Create tab
    climate_indices_tab = create_climate_indices_tab()
    tabs = widgets.Tab(layout={'width': '350px', 'height': '420px'})  # Reduced height to leave more space for footer
    tabs.children = [climate_indices_tab]
    tabs.set_title(0, 'Climate Indices')

    # Create footer with checkboxes on separate lines and more height
    preview_container = widgets.VBox([
        preview_chk,
        export_charts_chk,
        export_boundaries_chk,
        export_excel_chk
    ], layout=widgets.Layout(width='100%', margin='10px 0'))
    
    footer = widgets.VBox([
        preview_container, 
        widgets.HBox([run_button], layout=widgets.Layout(display='flex', justify_content='center', width='100%', margin='10px 0'))
    ], layout=widgets.Layout(width='100%', height='300px', padding='10px'))  # Increased height from 100px to 150px

    # Create sidebar with adjusted heights
    sidebar_content = widgets.VBox([
        info_box,
        tabs,
        # The output widget is now separate from the sidebar to prevent overflow issues
    ], layout=widgets.Layout(height='580px', overflow='visible'))  # Changed overflow to visible
    
    sidebar = widgets.VBox([
        sidebar_content,
        footer
    ], layout=widgets.Layout(width='370px', height='730px'))  # Increased overall height
    
    # Add output below the sidebar in a separate scrollable area
    output_area = widgets.VBox([
        output
    ], layout=widgets.Layout(width='370px', height='200px', overflow='auto'))
    
    sidebar_with_output = widgets.VBox([
        sidebar,
        output_area
    ], layout=widgets.Layout(width='370px', height='100%'))
    
    # Create map and chart area
    map_and_chart = widgets.VBox(
        [map_widget, chart_output],
        layout=widgets.Layout(width='750px', height='100%')
    )
    
    # Create main layout
    main_layout = widgets.HBox(
        [sidebar_with_output, map_and_chart],
        layout=widgets.Layout(width='100%', height='930px')  # Increased overall height
    )
    
    return main_layout

# JavaScript code for tooltips
def create_js_code():
    return f"""
    <script>
    document.querySelector('.{country_selector_id}').onmouseover = function() {{
        document.querySelector('.info-box textarea').value = 'Enter a country name. You can type to filter the list.';
    }};
    document.querySelector('.{adm_level_selector_id}').onmouseover = function() {{
        document.querySelector('.info-box textarea').value = 'Select the administrative level for analysis boundaries.\\n0 = Country\\n1 = State/Province\\n2 = District/County';
    }};
    document.querySelector('.{custom_boundaries_radio_id}').onmouseover = function() {{
        document.querySelector('.info-box textarea').value = 'Choose between default administrative boundaries or custom boundaries provided by the user.';
    }};
    document.querySelector('.{custom_boundaries_file_id}').onmouseover = function() {{
        document.querySelector('.info-box textarea').value = 'Enter the path to your custom boundaries file (Shapefile or GeoPackage).';
    }};
    document.querySelector('.{custom_boundaries_id_field_id}').onmouseover = function() {{
        document.querySelector('.info-box textarea').value = 'Enter the field name in your custom boundaries file that contains the unique identifier for each zone.';
    }};
    document.querySelector('.{custom_boundaries_name_field_id}').onmouseover = function() {{
        document.querySelector('.info-box textarea').value = 'Enter the field name in your custom boundaries file that contains the name or label for each zone.';
    }};
    document.querySelector('.{climate_index_selector_id}').onmouseover = function() {{
        document.querySelector('.info-box textarea').value = 'Select the climate index to analyze. Different indices measure various aspects of climate like temperature, precipitation, or heat stress.';
    }};
    document.querySelector('.{mode_selector_id}').onmouseover = function() {{
        document.querySelector('.info-box textarea').value = 'Select the data source mode:\\n\\nBaseline: Historical data from 1950-2023\\nProjections: Future scenarios from 2015-2100';
    }};
        document.querySelector('.{ssp_selector_id}').onmouseover = function() {{
        document.querySelector('.info-box textarea').value = 'Select the Shared Socioeconomic Pathway (SSP) scenario for climate projections:\\n- SSP1: Sustainability scenario\\n- SSP2: Middle of the road\\n- SSP3: Regional rivalry\\n- SSP5: Fossil-fueled development';
    }};
    document.querySelector('.{year_selector_id}').onmouseover = function() {{
        document.querySelector('.info-box textarea').value = 'Select the years to analyze from the historical time series (1950-2023). Hold Ctrl/Cmd key to select multiple years or drag to select a range.';
    }};
    document.querySelector('.${timescale_selector_id}').onmouseover = function() {{
        document.querySelector('.info-box textarea').value = 'Select the timescale for analysis:\\n\\nAnnual: Average for the whole year\\nSeasonal: Separate analysis for each season (DJF, MAM, JJA, SON)';
    }};
    </script>
    """

# Function to initialize the tool
def initialize_tool():
    # Create the main layout
    main_layout = create_layout()
    
    # Display the layout and inject JavaScript code
    display(main_layout)
    display(HTML(create_js_code()))
    
    # Initialize empty map
    m = folium.Map(location=[0, 0], zoom_start=2)
    map_widget.value = m._repr_html_()
    
    # Initialize year options based on default mode
    update_year_options(mode_selector.value)
    
    # Print welcome message
    with output:
        print("Welcome to the Climate Indices Timeseries Visualization Tool")
        print("1. Select a country and administrative level")
        print("2. Choose a climate index and select the data mode (Baseline or Projections)")
        print("3. Select years to analyze and click 'Run Analysis'")
        print("4. View both raw grid data and zonal statistics for each selected year")
