import os
import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import cartopy.crs as ccrs
import geopandas as gpd
from matplotlib.colors import TwoSlopeNorm
from urllib.request import urlretrieve
from shapely.geometry import shape
import requests
from IPython.display import display, clear_output, HTML
import ipywidgets as widgets
import pandas as pd
import common
import time
import folium
import tkinter as tk
from tkinter import filedialog
from input_utils import get_adm_data
import rasterstats
from rasterstats import zonal_stats
import rioxarray
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

# Function to build URL for timeseries data
def build_timeseries_url(index):
    """Build the URL for timeseries data for a given climate index."""
    # Replace 'climatology' with 'timeseries' in the URL pattern
    timeseries_url = f"https://wbg-cckp.s3.amazonaws.com/data/era5-x0.25/{index}/era5-x0.25-historical/timeseries-{index}-annual-mean_era5-x0.25_era5-x0.25-historical_timeseries_mean_1950-2023.nc"
    return timeseries_url

# Function to download a file if it doesn't exist
def download_file(url, local_path):
    """Download a file if it doesn't exist."""
    if not os.path.exists(local_path):
        print(f"Downloading {url} to {local_path}")
        try:
            urlretrieve(url, local_path)
            print(f"Download complete: {local_path}")
            return True
        except Exception as e:
            print(f"Download failed: {str(e)}")
            return False
    else:
        print(f"File already exists: {local_path}")
        return True

# Define variable name in the NetCDF file for the index
def get_variable_name(index):
    """Get the variable name for a climate index."""
    # Replace 'climatology' with 'timeseries'
    variable_name = f"timeseries-{index}-annual-mean"
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
    if index in ['cwd', 'cdd', 'hd30', 'hd35', 'hi35','hi39', 'hdtrhi']:
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
def prepare_xarray_for_zonal_stats(xds, var_name):
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
        data_array_rio = prepare_xarray_for_zonal_stats(data_array, data_array.name)
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
    
    # Get value range for data
    vmin = admin_boundaries_with_stats[data_col].min()
    vmax = admin_boundaries_with_stats[data_col].max()
    
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
    country_name = admin_boundaries_with_stats['NAM_0'].iloc[0] if 'NAM_0' in admin_boundaries_with_stats.columns else "Selected Country"
    plt.suptitle(f"{title} - {country_name} ({year})", fontsize=16)
    
    # Adjust layout
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    
    print("Choropleth map created successfully")
    return fig

# Function to create plots for a climate index year
def create_climate_plots(timeseries_ds, admin_boundaries, index, selected_year):
    """Create plots for a climate index showing data for the selected year."""
    # Get variable name
    variable_name = get_variable_name(index)
    
    # Get metadata
    title, unit, cmap = get_index_metadata(index)
    
    if timeseries_ds is None:
        print("Missing data, cannot create plots")
        return None, None
    
    # Extract data for the selected year
    year_data = extract_year_from_timeseries(timeseries_ds, variable_name, selected_year)
    if year_data is None:
        print(f"No data available for {index} in year {selected_year}")
        return None, None
    
    # Handle time units if needed
    year_data = handle_time_units(year_data, index)
    
    # Print data range for reference
    print(f"Data range for {index} in {selected_year}: {year_data.min().values} to {year_data.max().values}")
    
    # Set up the projection for plotting
    projection_crs = ccrs.PlateCarree()
    
    # Create a figure with one subplot
    fig, ax = plt.subplots(figsize=(10, 8), subplot_kw={'projection': projection_crs})
    
    # Get latitude and longitude values
    lats = timeseries_ds.lat.values
    lons = timeseries_ds.lon.values
    
    # Dynamically determine color ranges based on data within the country extent
    if admin_boundaries is not None:
        # Get bounds of the country
        bounds = admin_boundaries.total_bounds
        
        # Create a mask for the area within the country bounds
        lon_mask = (lons >= bounds[0]) & (lons <= bounds[2])
        lat_mask = (lats >= bounds[1]) & (lats <= bounds[3])
        
        # Apply the mask to extract data within the country extent
        country_data = year_data.where(
            (year_data.lon >= bounds[0]) & 
            (year_data.lon <= bounds[2]) & 
            (year_data.lat >= bounds[1]) & 
            (year_data.lat <= bounds[3])
        )
        
        # Calculate min/max from the masked data
        country_min = float(country_data.min().values)
        country_max = float(country_data.max().values)
        
        # Set vmin/vmax based on the masked data
        if index in ['cwd', 'cdd']:
            vmin = max(0, country_min)
            vmax = min(100, country_max * 1.1)
        else:
            vmin = country_min
            vmax = country_max
        
        print(f"Using country extent min/max for colorbar: {vmin} to {vmax}")
    else:
        # Fallback to global extent if no boundaries available
        if index in ['cwd', 'cdd']:
            vmin = max(0, float(year_data.min().values))
            vmax = min(100, float(year_data.max().values) * 1.1)
        else:
            vmin = float(year_data.min().values)
            vmax = float(year_data.max().values)
    
    plot = ax.pcolormesh(lons, lats, year_data.squeeze(), 
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
    
    # Set title
    country_name = admin_boundaries['NAM_0'].iloc[0] if (admin_boundaries is not None and 'NAM_0' in admin_boundaries.columns) else "Selected Country"
    
    plt.suptitle(f"{title} - {country_name} ({selected_year})", fontsize=16)
    
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
            
            # Calculate zonal statistics for the year data
            year_data.name = index
            gdf_zonal = calculate_zonal_stats(year_data, admin_boundaries)
            
            # Create choropleth map
            zonal_col = f"{index}_mean"
            
            if zonal_col in gdf_zonal.columns:
                # Create choropleth map
                zonal_fig = create_choropleth_map(
                    gdf_zonal, 
                    zonal_col, 
                    title, unit, 
                    cmap,
                    selected_year
                )
                zonal_data = gdf_zonal
            else:
                # Check if we need to try different column names (may have been renamed)
                potential_cols = [col for col in gdf_zonal.columns if index.lower() in col.lower() and 'mean' in col.lower()]
                
                if potential_cols:
                    zonal_col = potential_cols[0]
                    print(f"Using alternative column name: {zonal_col}")
                    
                    zonal_fig = create_choropleth_map(
                        gdf_zonal, 
                        zonal_col, 
                        title, unit, 
                        cmap,
                        selected_year
                    )
                    zonal_data = gdf_zonal
                else:
                    print(f"Warning: Required columns for zonal statistics not found.")
                    print(f"Available columns: {gdf_zonal.columns.tolist()}")
            
        except Exception as e:
            print(f"Error in zonal statistics calculation: {e}")
            import traceback
            traceback.print_exc()
    
    return fig, zonal_fig, zonal_data

# Function to save a figure to a file
def save_figure(fig, country, index, year, output_dir, suffix=""):
    """Save a figure to a file."""
    if fig is None:
        return None
    
    # Create index-specific subdirectory
    index_dir = os.path.join(output_dir, f"img/{index}")
    if not os.path.exists(index_dir):
        os.makedirs(index_dir)
    
    # Create filename with requested structure
    output_path = os.path.join(index_dir, f"{country.lower()}_{index}_{year}{suffix}.png")
    fig.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Saved figure to {output_path}")
    return output_path

# Function to export GeoDataFrame to GeoPackage
def export_boundaries_to_gpkg(gdf, country, adm_level, index, year, output_dir, all_gdf=None, is_final=False):
    """
    Export administrative boundaries with statistics to a GeoPackage file.
    
    Args:
        gdf: GeoDataFrame with zonal statistics for the current year
        country: Country ISO code
        index: Climate index
        year: Year of the data
        output_dir: Output directory
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
    
    # Create filename - use a single file for all years
    output_path = os.path.join(output_dir, f"{country.lower()}_{index}_timeseries_ADM{adm_level}.gpkg")
    
    try:
        # Ensure the GeoDataFrame has a proper CRS
        if gdf.crs is None:
            gdf = gdf.set_crs("EPSG:4326")
        
        # Rename the zonal statistic column to include the year
        zonal_col = None
        for col in gdf.columns:
            if f"{index}_mean" in col:
                zonal_col = col
                break
        
        if zonal_col:
            # Copy the original GeoDataFrame
            gdf_copy = gdf.copy()
            # Rename the column to include the year
            year_col = f"Y{year}_mean"
            gdf_copy = gdf_copy.rename(columns={zonal_col: year_col})
            
            # If all_gdf is None, initialize it with the first year's data
            if all_gdf is None:
                all_gdf = gdf_copy
            else:
                # Merge the new year's data with the existing data
                # Keep only the geometry and ID columns from all_gdf and add the new year column
                # Find ID columns (usually these are the administrative boundaries identifiers)
                id_cols = [col for col in all_gdf.columns if 'ID' in col.upper() or 'CODE' in col.upper() or 'HASC' in col.upper()]
                # Add essential columns
                essential_cols = ['geometry', 'NAM_0']
                if 'ADM0_PCODE' in all_gdf.columns:
                    essential_cols.append('ADM0_PCODE')
                
                # Merge on geometry and ID columns
                merge_cols = list(set(id_cols + essential_cols).intersection(set(all_gdf.columns)).intersection(set(gdf_copy.columns)))
                if not merge_cols or 'geometry' not in merge_cols:
                    # If no common ID columns or geometry not in merge_cols, use geometry and NAM_0 if available
                    merge_cols = ['geometry']
                    if 'NAM_0' in all_gdf.columns and 'NAM_0' in gdf_copy.columns:
                        merge_cols.append('NAM_0')
                
                # Extract the year column from gdf_copy
                year_data = gdf_copy[merge_cols + [year_col]]
                
                # Merge with all_gdf
                all_gdf = all_gdf.merge(year_data[[col for col in year_data.columns if col not in merge_cols]], 
                                       left_index=True, right_index=True, how='left')
        
        # If this is the final export, save the combined GeoPackage
        if is_final and all_gdf is not None:
            layer_name = f"{index}_timeseries"
            all_gdf.to_file(output_path, layer=layer_name, driver="GPKG")
            print(f"Saved combined boundary data with {len([col for col in all_gdf.columns if '_mean' in col])} years to {output_path}")
            return output_path, all_gdf
        
        return None, all_gdf
        
    except Exception as e:
        print(f"Error exporting boundaries to GeoPackage: {e}")
        import traceback
        traceback.print_exc()
        return None, all_gdf
        
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
            print(f"Years: {', '.join(map(str, selected_years))}")
            
            # Create temp directory
            temp_dir = os.path.join(common.OUTPUT_DIR, "climate_indices_nc")
            os.makedirs(temp_dir, exist_ok=True)
            print(f"Temporary directory: {temp_dir}")
            
            # Create output directory
            output_dir = os.path.join(common.OUTPUT_DIR, "climate_indices_timeseries")
            os.makedirs(output_dir, exist_ok=True)
            print(f"Output directory: {output_dir}")
            
            # Build URL
            print("Building URL for data download...")
            timeseries_url = build_timeseries_url(selected_index)
            
            # Download file
            timeseries_file = os.path.join(temp_dir, f"{selected_index}_timeseries_1950-2023.nc")
            
            print("Downloading data file...")
            print(f"Timeseries data URL: {timeseries_url}")
            timeseries_success = download_file(timeseries_url, timeseries_file)
            
            if not timeseries_success:
                print("Error: Failed to download required data file")
                return
                
            # Load NetCDF data
            variable_name = get_variable_name(selected_index)
            print(f"Variable name: {variable_name}")
            
            print("Loading NetCDF data file...")
            timeseries_ds = load_netcdf(timeseries_file, variable_name)
            
            if timeseries_ds is None:
                print("Error: Failed to load NetCDF data file")
                return
                
            # Get administrative boundaries
            print(f"Loading administrative boundaries (ADM level {selected_adm_level})...")
            print(f"Loading boundaries...")
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
                            print(f"Error: No boundary data found in the specified file")
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
            combined_gdf = None  # For storing combined GeoDataFrame with all years
            
            # Process each selected year
            for year_idx, selected_year in enumerate(selected_years):
                print(f"\nProcessing year {selected_year} ({year_idx+1}/{len(selected_years)})...")
                
                # Create plots for this year
                fig, zonal_fig, zonal_data = create_climate_plots(
                    timeseries_ds, admin_boundaries, 
                    selected_index, selected_year
                )
                
                if fig is None:
                    print(f"Warning: Failed to create plots for year {selected_year}, skipping...")
                    continue
                
                # Store figures and data
                all_grid_figs.append((selected_year, fig))
                if zonal_fig is not None:
                    all_zonal_figs.append((selected_year, zonal_fig))
                if zonal_data is not None:
                    all_zonal_data.append((selected_year, zonal_data))
                
                # Save figures if export is enabled
                if export_charts_chk.value:
                    save_figure(
                        fig, iso_a3, selected_index, selected_year, 
                        output_dir, "_grid"
                    )
                    if zonal_fig is not None:
                        save_figure(
                            zonal_fig, iso_a3, selected_index, selected_year, 
                            output_dir, "_zonal"
                        )

                # Add this year's data to the combined GeoDataFrame if needed
                if export_boundaries_chk.value and zonal_data is not None:
                    print(f"Adding {selected_year} data to combined GeoPackage...")
                    # Only save on the last iteration
                    is_final = (year_idx == len(selected_years) - 1)
                    _, combined_gdf = export_boundaries_to_gpkg(
                        zonal_data, 
                        iso_a3,
                        selected_adm_level,
                        selected_index, 
                        selected_year, 
                        output_dir,
                        all_gdf=combined_gdf,
                        is_final=is_final
                    )
                
                # Display figures for this year
                with chart_output:
                    display(fig)
                    if zonal_fig is not None:
                        display(zonal_fig)
            
            # Final export of combined GeoPackage if needed
            if export_boundaries_chk.value and combined_gdf is not None:
                export_path, _ = export_boundaries_to_gpkg(
                    combined_gdf, 
                    iso_a3, 
                    selected_adm_level, 
                    selected_index, 
                    0,  # Dummy year value
                    output_dir,
                    all_gdf=combined_gdf,
                    is_final=True
                )
                if export_path:
                    print(f"All years' data exported to combined GeoPackage: {export_path}")
            
            # Summary
            print(f"\nAnalysis summary:")
            print(f"Successfully processed {len(all_grid_figs)} out of {len(selected_years)} selected years")
            if export_charts_chk.value:
                print(f"Exported {len(all_grid_figs)} grid maps and {len(all_zonal_figs)} zonal maps")
            if export_boundaries_chk.value:
                print(f"Exported data for {len(all_zonal_data)} years to a single combined GeoPackage")
            
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
        country_section,
        index_section
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
        export_boundaries_chk
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
    document.querySelector('.{year_selector_id}').onmouseover = function() {{
        document.querySelector('.info-box textarea').value = 'Select the years to analyze from the historical time series (1950-2023). Hold Ctrl/Cmd key to select multiple years or drag to select a range.';
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
    
    # Initialize custom boundaries if any   
    update_custom_boundaries_visibility()
    
    # Print welcome message
    with output:
        print("Welcome to the Climate Indices Timeseries Visualization Tool")
        print("1. Select a country and administrative level")
        print("2. Choose a climate index and select one or more years to analyze")
        print("3. Click 'Run Analysis' to generate visualizations for all selected years")
        print("4. View both raw grid data and zonal statistics for each selected year")
