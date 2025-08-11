# Check SSL limitations
import sys
sys.path.append('.')  # Ensure the current directory is in the path
try:
    from ssl_utils import disable_ssl_verification
    disable_ssl_verification()
except ImportError:
    import ssl
    import warnings
    import urllib3
    
    # Fallback if ssl_utils.py is not available
    warnings.filterwarnings('ignore', message='Unverified HTTPS request')
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    try:
        ssl._create_default_https_context = ssl._create_unverified_context
    except AttributeError:
        pass

# Import necessary libraries
import leafmap.foliumap as leafmap
import geopandas as gpd
import ipywidgets as widgets
from IPython.display import display, HTML
from ipyleaflet import Map, basemap_to_tiles, basemaps, LayersControl, GeoJSON, LegendControl, WidgetControl
from IPython.display import display, clear_output, HTML
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import branca.colormap as cm
import numpy as np
import pandas as pd
import time
import tkinter as tk
from tkinter import filedialog
import rasterio
import os
import sys
import re
from sympy import sympify, symbols
import math
import multiprocessing as mp
import gc

import common
from input_utils import get_adm_data
import notebook_utils
from runAnalysis import (
    plot_results, create_summary_df, prepare_excel_gpkg_files,
    prepare_sheet_name, saving_excel_and_gpgk_file, prepare_and_save_summary_df
)
from custom_hazard_analysis import run_analysis_with_custom_hazard

# Define hazard type
haz_type = 'CUSTOM'

# Create an HTML widget to display the map
map_widget = widgets.Output(layout=widgets.Layout(width='98%', height='600px'))

m = None  # global map object
basemaps_dict = {}
current_hazard_layer = None
current_info_control = None
current_legend_control = None

# Load country data
df = pd.read_csv('countries.csv')
country_dict = dict(zip(df['NAM_0'], df['ISO_A3']))
iso_to_country = dict(zip(df['ISO_A3'], df['NAM_0']))

# Create the Combobox widget with auto-complete functionality
country_selector = notebook_utils.create_country_selector_widget(list(country_dict.keys()))
country_selector_id = f'country-selector-{id(country_selector)}'
country_selector.add_class(country_selector_id)

# Define a function to handle changes in the combobox
def on_country_change(change):
    with output:
        output.clear_output()
        adm_level_selector.value = None
        notebook_utils.on_country_change(
            change, country_dict, get_adm_data, plot_geospatial_boundaries
        )

# Attach the function to the combobox
country_selector.observe(on_country_change, names='value')

# Administrative level boundaries
adm_level_selector = notebook_utils.adm_level_selector
adm_level_selector_id = f'adm-level-selector-{id(adm_level_selector)}'
adm_level_selector.add_class(adm_level_selector_id)

def on_adm_level_change(change):
    notebook_utils.on_adm_level_change(
        change, country_selector, country_dict,
        get_adm_data, plot_geospatial_boundaries
    )

# Create a new dropdown for zonal statistics criteria
zonal_stats_selector = widgets.Dropdown(
    options=[
        ('Sum', 'sum'),
        ('Mean', 'mean'),
        ('Max', 'max')
    ],
    value='sum',
    description='Zonal stats:',
    disabled=False,
    layout=widgets.Layout(width='250px')
)
zonal_stats_selector_id = f'zonal-stats-selector-{id(zonal_stats_selector)}'
zonal_stats_selector.add_class(zonal_stats_selector_id)

# Update the plot_geospatial_boundaries function to use ipyleaflet
def plot_geospatial_boundaries(gdf, crs: str = "EPSG:4326"):
    from ipyleaflet import GeoJSON
    from math import log
    global m, basemaps_dict, current_hazard_layer

    gdf = gdf.set_crs(crs)  # Assign WGS 84 CRS by default

    with map_widget:
        map_widget.clear_output(wait=True)

        # Remove only the admin boundary layers, not the basemap or hazard layers
        admin_layers = [layer for layer in m.layers if hasattr(layer, 'name') and layer.name == "Administrative Boundaries"]
        for layer in admin_layers:
            m.remove_layer(layer)

        # Add the GeoJSON layer
        geo_json = GeoJSON(
            data=gdf.__geo_interface__,
            style={
                'opacity': 1, 
                'fillOpacity': 0.0, 
                'weight': 1, 
                'color': 'black'
            },
            name="Administrative Boundaries"
        )
        m.add(geo_json)

        # Center the map on the boundaries
        bounds = gdf.total_bounds
        m.center = ((bounds[1] + bounds[3]) / 2, (bounds[0] + bounds[2]) / 2)

        # Estimate zoom level
        def get_approx_zoom(bounds, map_width_pixels=800):
            west, south, east, north = bounds
            lat_diff = abs(north - south)
            lon_diff = abs(east - west)
            max_diff = max(lat_diff, lon_diff)
            if max_diff == 0:
                return 15  # arbitrary close zoom for point
            zoom = min(int(log(360 / max_diff) / log(2)), 18)
            return max(1, zoom)

        m.zoom = get_approx_zoom(bounds)

        display(m)

# Custom Adm data
# Add these to your existing UI elements
custom_boundaries_radio = notebook_utils.custom_boundaries_radio
custom_boundaries_radio_id = f'custom-boundaries-radio-{id(custom_boundaries_radio)}'
custom_boundaries_radio.add_class(custom_boundaries_radio_id)

custom_boundaries_file = notebook_utils.custom_boundaries_file
custom_boundaries_file_id = f'custom-boundaries-file-{id(custom_boundaries_file)}'
custom_boundaries_file.add_class(custom_boundaries_file_id)

custom_boundaries_id_field = widgets.Dropdown(
    options=[],
    value=None,
    description='ID field:',
    disabled=True,
    layout=widgets.Layout(width='250px')
)
custom_boundaries_id_field_id = f'custom-boundaries-id-field-{id(custom_boundaries_id_field)}'
custom_boundaries_id_field.add_class(custom_boundaries_id_field_id)

custom_boundaries_name_field = widgets.Dropdown(
    options=[],
    value=None,
    description='Name field:',
    disabled=True,
    layout=widgets.Layout(width='250px')
)
custom_boundaries_name_field_id = f'custom-boundaries-name-field-{id(custom_boundaries_name_field)}'
custom_boundaries_name_field.add_class(custom_boundaries_name_field_id)

select_file_button = notebook_utils.select_file_button

# Custom ADM Functions
def select_file(b):
    notebook_utils.select_file(b, update_preview_map)

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
            plot_geospatial_boundaries(gdf)
            notebook_utils.set_default_values(gdf, custom_boundaries_id_field, custom_boundaries_name_field)
        except Exception as e:
            print(f"Error loading custom boundaries: {str(e)}")
    elif country_selector.value:
        country = country_dict.get(country_selector.value)
        adm_level = adm_level_selector.value
        try:
            # If no ADM level is selected, default to level 0 (country boundaries)
            level = adm_level if adm_level is not None else 0
            gdf = get_adm_data(country, level)
            plot_geospatial_boundaries(gdf)
        except Exception as e:
            print(f"Error loading boundaries: {str(e)}")

# Attach the functions to the widgets
country_selector.observe(on_country_change, names='value')
adm_level_selector.observe(on_adm_level_change, names='value')

# Custom Hazard File Selector
hazard_file_selector = widgets.Text(
    value='',
    placeholder='Enter path to hazard raster file',
    description='Hazard raster:',
    disabled=False,
    layout=widgets.Layout(width='250px')
)
hazard_file_selector_id = f'hazard-file-selector-{id(hazard_file_selector)}'
hazard_file_selector.add_class(hazard_file_selector_id)

select_hazard_button = widgets.Button(
    description='Select Hazard File',
    disabled=False,
    button_style='info',
    tooltip='Click to select a hazard raster file',
    icon='file',
    layout=widgets.Layout(width='150px')
)

# Function to select hazard file
def select_hazard_file(b):
    root = tk.Tk()
    root.withdraw()
    root.attributes('-topmost', True)
    file_path = filedialog.askopenfilename(
        title="Select Hazard Raster",
        filetypes=[("GeoTIFF", "*.tif"), ("All Files", "*.*")],
        parent=root
    )
    if file_path:
        hazard_file_selector.value = file_path
        # Update the preview or show hazard details
        preview_hazard_data()
    root.destroy()

select_hazard_button.on_click(select_hazard_file)

# Hazard name for output files
hazard_name_input = widgets.Text(
    value='',
    placeholder='Enter a name for this hazard (e.g., flood_depth)',
    description='Hazard name:',
    disabled=False,
    layout=widgets.Layout(width='250px')
)
hazard_name_input_id = f'hazard-name-input-{id(hazard_name_input)}'
hazard_name_input.add_class(hazard_name_input_id)

# Hazard threshold
hazard_threshold_slider = widgets.FloatSlider(
    value=0.0,
    min=0.0,
    max=100.0,
    step=0.1,
    description='Min threshold:',
    disabled=False,
    continuous_update=False,
    orientation='horizontal',
    readout=True,
    readout_format='.1f',
    layout=widgets.Layout(width='250px')
)
hazard_threshold_slider_id = f'hazard-threshold-slider-{id(hazard_threshold_slider)}'
hazard_threshold_slider.add_class(hazard_threshold_slider_id)

# Hazard Return Period
return_period_input = widgets.Text(
    value='100',
    placeholder='Enter return period (e.g., 100)',
    description='Return period:',
    disabled=False,
    layout=widgets.Layout(width='250px')
)
return_period_input_id = f'return-period-input-{id(return_period_input)}'
return_period_input.add_class(return_period_input_id)

# Multiple return periods selector for probabilistic analysis
use_multi_rp = widgets.Checkbox(
    value=False,
    description='Multiple return periods',
    disabled=False,
    indent=False,
    layout=widgets.Layout(width='250px')
)
use_multi_rp_id = f'use-multi-rp-{id(use_multi_rp)}'
use_multi_rp.add_class(use_multi_rp_id)

# Container for multiple hazard files
multi_hazard_container = widgets.VBox([])

# Function to update multiple return periods UI
def update_multi_rp_ui(*args):
    multi_hazard_container.children = []
    if use_multi_rp.value:
        # Show UI for multiple return periods
        return_period_input.disabled = True
        hazard_file_selector.disabled = True
        select_hazard_button.disabled = True
        
        # Create default return periods
        default_rps = [10, 20, 50, 100, 200, 500, 1000]
        
        # Create a title
        title = widgets.HTML("<b>Multiple Hazard Rasters for Different Return Periods</b>")
        multi_hazard_container.children = (title,)
        
        # Create entries for each return period
        for rp in default_rps:
            rp_text = widgets.Text(
                value=str(rp),
                description=f'RP:',
                disabled=False,
                layout=widgets.Layout(width='80px')
            )
            
            file_text = widgets.Text(
                value='',
                placeholder=f'Path to RP {rp} hazard raster',
                disabled=False,
                layout=widgets.Layout(width='200px')
            )
            
            file_button = widgets.Button(
                description='Select',
                disabled=False,
                button_style='info',
                layout=widgets.Layout(width='80px')
            )
            
            # Create a closure to capture the file_text reference
            def create_on_click(file_text_widget):
                def on_click(b):
                    root = tk.Tk()
                    root.withdraw()
                    root.attributes('-topmost', True)
                    file_path = filedialog.askopenfilename(
                        title=f"Select Hazard Raster",
                        filetypes=[("GeoTIFF", "*.tif"), ("All Files", "*.*")],
                        parent=root
                    )
                    if file_path:
                        file_text_widget.value = file_path
                    root.destroy()
                return on_click
            
            file_button.on_click(create_on_click(file_text))
            
            row = widgets.HBox([rp_text, file_text, file_button])
            multi_hazard_container.children = multi_hazard_container.children + (row,)
    else:
        # Show UI for single return period
        return_period_input.disabled = False
        hazard_file_selector.disabled = False
        select_hazard_button.disabled = False

use_multi_rp.observe(update_multi_rp_ui, 'value')

# Hazard preview output
hazard_preview = widgets.Output(layout=widgets.Layout(width='280px', height='250px'))

def preview_hazard_data():
    import os, re, rasterio
    import numpy as np
    import geopandas as gpd
    from IPython.display import display, clear_output
    from ipyleaflet import GeoJSON, LayersControl, LegendControl, WidgetControl, TileLayer
    from ipywidgets import HTML
    from localtileserver import TileClient, get_leaflet_tile_layer
    import matplotlib.pyplot as plt
    import matplotlib.colors as mcolors
    from io import BytesIO
    import base64

    global m, basemaps_dict, current_hazard_layer, current_info_control, current_legend_control

    with hazard_preview:
        clear_output(wait=True)
        file_path = hazard_file_selector.value
        if not file_path or not os.path.exists(file_path):
            print("Please select a valid hazard raster file.")
            return

        try:
            with rasterio.open(file_path) as src:
                width = src.width
                height = src.height
                count = src.count
                dtype = src.dtypes[0]
                nodata = src.nodata
                bounds = src.bounds

                window_height = min(500, height)
                window_width = min(500, width)
                window = ((0, window_height), (0, window_width))
                sample = src.read(1, window=window)

                if nodata is not None:
                    valid_mask = (sample != nodata) & ~np.isnan(sample)
                else:
                    valid_mask = ~np.isnan(sample)

                zero_mask = sample == 0
                analysis_mask = valid_mask & ~zero_mask
                valid_sample = sample[analysis_mask]

                if len(valid_sample) > 0:
                    min_val = np.min(valid_sample)
                    max_val = np.max(valid_sample)
                    mean_val = np.mean(valid_sample)

                    print(f"Hazard raster dimensions: {width} x {height}")
                    print(f"Number of bands: {count}")
                    print(f"Data type: {dtype}")
                    print(f"NoData value: {nodata}")
                    zeros_count = np.sum(zero_mask & valid_mask)
                    print(f"Zero values: {zeros_count} ({zeros_count/sample.size*100:.1f}% of total)")
                    print(f"Value range (excluding zeros): {min_val:.4f} to {max_val:.4f}")
                    print(f"Mean value (excluding zeros): {mean_val:.4f}")

                    hazard_threshold_slider.max = float(max_val * 1.2)
                    hazard_threshold_slider.value = float(min_val * 0.5)

                    if not hazard_name_input.value:
                        base_name = os.path.basename(file_path)
                        name_no_ext = os.path.splitext(base_name)[0]
                        clean_name = re.sub(r'[^a-zA-Z0-9_]', '_', name_no_ext)
                        hazard_name_input.value = clean_name
                else:
                    print("No valid non-zero data found in the sample.")
                    return

            with map_widget:
                map_widget.clear_output(wait=True)

                # Remove previous hazard layer and controls if they exist
                if current_hazard_layer:
                    if current_hazard_layer in m.layers:
                        m.remove_layer(current_hazard_layer)
                if current_info_control:
                    m.remove_control(current_info_control)
                if current_legend_control:
                    m.remove_control(current_legend_control)

                # Get admin boundaries if available
                admin_gdf = None
                if country_selector.value:
                    try:
                        country = country_dict.get(country_selector.value, None)
                        if country and custom_boundaries_radio.value == 'Default boundaries':
                            adm_level = adm_level_selector.value if adm_level_selector.value is not None else 0
                            admin_gdf = get_adm_data(country, adm_level)
                        elif custom_boundaries_radio.value == 'Custom boundaries' and os.path.exists(custom_boundaries_file.value):
                            admin_gdf = gpd.read_file(custom_boundaries_file.value)

                        if admin_gdf is not None:
                            # Check if admin boundaries already exist
                            existing_admin = [layer for layer in m.layers if hasattr(layer, 'name') and layer.name == "Administrative Boundaries"]
                            if not existing_admin:
                                geo_json = GeoJSON(
                                    data=admin_gdf.__geo_interface__,
                                    style={
                                        'opacity': 1, 
                                        'fillOpacity': 0.0, 
                                        'weight': 1, 
                                        'color': 'black'
                                    },
                                    name="Administrative Boundaries"
                                )
                                m.add(geo_json)

                            bounds = admin_gdf.total_bounds
                            m.center = ((bounds[1] + bounds[3])/2, (bounds[0] + bounds[2])/2)

                            from math import log
                            def get_approx_zoom(bounds, map_width_pixels=800):
                                west, south, east, north = bounds
                                lat_diff = abs(north - south)
                                lon_diff = abs(east - west)
                                max_diff = max(lat_diff, lon_diff)
                                if max_diff == 0:
                                    return 15
                                zoom = min(int(log(360 / max_diff) / log(2)), 18)
                                return max(1, zoom)

                            m.zoom = get_approx_zoom(bounds)
                    except Exception as e:
                        print(f"Could not add boundaries to map: {str(e)}")

                client = TileClient(file_path)

                # Process a larger sample for color range determination
                with rasterio.open(file_path) as src:
                    read_window = ((0, min(1000, height)), (0, min(1000, width)))
                    larger_sample = src.read(1, window=read_window)

                    if nodata is not None:
                        valid_data = larger_sample[(larger_sample != nodata) & ~np.isnan(larger_sample)]
                    else:
                        valid_data = larger_sample[~np.isnan(larger_sample)]

                    if len(valid_data) > 0:
                        # Use percentiles for better color range
                        vmin, vmax = np.percentile(valid_data, [2, 98])
                    else:
                        vmin, vmax = 0, 1

                    # Choose appropriate colormap
                    cmap_name = 'coolwarm' if np.any(valid_data < 0) else 'plasma'
                    print(f"Using {cmap_name} colormap with range: {vmin:.4f} to {vmax:.4f}")

                # Create the tile layer
                tile_layer = get_leaflet_tile_layer(
                    client,
                    name="Hazard Raster",
                    opacity=0.7,
                    nodata=nodata,
                    cmap=cmap_name,
                    vmin=vmin, 
                    vmax=vmax
                )
                
                # Store the current layer for later removal
                current_hazard_layer = tile_layer
                m.add(tile_layer)

                # Create a colorbar legend
                fig = plt.figure(figsize=(1.5, 4))
                ax = fig.add_axes([0.3, 0.05, 0.2, 0.9])
                
                # Create the colormap
                cmap = plt.get_cmap(cmap_name)
                norm = mcolors.Normalize(vmin=vmin, vmax=vmax)
                
                # Create the colorbar
                cb = plt.colorbar(plt.cm.ScalarMappable(norm=norm, cmap=cmap), 
                                 cax=ax, orientation='vertical')
                
                # Get the hazard name for the colorbar label
                hazard_name = hazard_name_input.value or os.path.basename(file_path)
                cb.set_label(f"{hazard_name} intensity")
                
                # Save the colorbar to a BytesIO object
                buf = BytesIO()
                fig.savefig(buf, format='png', bbox_inches='tight', transparent=True)
                buf.seek(0)
                plt.close(fig)
                
                # Create a data URL
                data_url = f"data:image/png;base64,{base64.b64encode(buf.getvalue()).decode('utf-8')}"
                
                # Create a widget with the legend image
                legend_html = f"""
                <div style="
                    background-color: white;
                    padding: 5px;
                    border-radius: 5px;
                    box-shadow: 0 0 5px rgba(0,0,0,0.3);
                ">
                    <img src="{data_url}" style="height:200px;">
                </div>
                """
                legend_widget = HTML(value=legend_html)
                legend_control = WidgetControl(widget=legend_widget, position='bottomright')
                
                # Add the legend to the map
                m.add_control(legend_control)
                current_legend_control = legend_control

                if admin_gdf is None:
                    m.center = client.center()
                    m.zoom = client.default_zoom

                display(m)

            print("Map updated successfully with hazard data and legend.")

        except Exception as e:
            print(f"Error reading hazard file: {str(e)}")
            import traceback
            traceback.print_exc()

        
# Connect hazard file selector to preview function
hazard_file_selector.observe(lambda change: preview_hazard_data() if change['name'] == 'value' else None, names='value')

# Exposure
exposure_selector = notebook_utils.exposure_selector
exposure_selector_id = f'exposure-selector-{id(exposure_selector)}'
exposure_selector.add_class(exposure_selector_id)

## Custom exposure
custom_exposure_container = widgets.VBox([])
custom_exposure_radio = widgets.RadioButtons(options=['Default exposure', 'Custom exposure'], layout=widgets.Layout(width='250px'))
custom_exposure_radio_id = f'custom-exposure-radio-{id(custom_exposure_radio)}'
custom_exposure_radio.add_class(custom_exposure_radio_id)
custom_exposure_textbox = widgets.Text(value='', placeholder='Enter filename (without extension)', layout=widgets.Layout(width='250px'))
custom_exposure_textbox_id = f'custom-exposure-textbox-{id(custom_exposure_textbox)}'
custom_exposure_textbox.add_class(custom_exposure_textbox_id)

# Function to update custom exposure textboxes
def update_custom_exposure_textboxes(*args):
    custom_exposure_container.children = []
    if custom_exposure_radio.value == 'Custom exposure':
        for exp in exposure_selector.value:
            textbox = widgets.Text(
                value='',
                placeholder=f'Enter filename for {exp} (without extension)',
                layout=widgets.Layout(width='250px')
            )
            custom_exposure_container.children += (textbox,)

# Update the custom exposure visibility function
def update_custom_exposure_visibility(*args):
    custom_exposure_container.layout.display = 'none' if custom_exposure_radio.value == 'Default exposure' else 'block'
    update_custom_exposure_textboxes()

exposure_selector.observe(update_custom_exposure_textboxes, 'value')
custom_exposure_radio.observe(update_custom_exposure_visibility, 'value')    

# Vulnerability approach
approach_box = widgets.Output(layout=widgets.Layout(width='280px', height='250px'))

# Modified approach selector to only include Function and Classes
approach_selector = widgets.Dropdown(
    options=[
        ('Function', 'Function'),
        ('Classes', 'Classes')
    ],
    value='Function',
    description='Approach:',
    disabled=False,
    layout=widgets.Layout(width='250px')
)
approach_selector_id = f'approach-selector-{id(approach_selector)}'
approach_selector.add_class(approach_selector_id)

# Function input field
custom_function_input = widgets.Text(
    value='Y = min(1.0, X/10.0)',
    placeholder='Enter function (e.g., Y = 0.01*X or Y = 1-exp(-0.1*X))',
    description='Function:',
    disabled=False,
    layout=widgets.Layout(width='250px')
)
custom_function_input_id = f'custom-function-input-{id(custom_function_input)}'
custom_function_input.add_class(custom_function_input_id)

custom_function_description = widgets.HTML(
    value='''<p style="font-size: 0.8em;">
    Define your function using X as the hazard variable and Y as the impact factor.<br>
    Example: Y = 1-exp(-0.1*X) for exponential damage relationship.<br>
    Function should return values between 0 and 1.
    </p>''',
    layout=widgets.Layout(width='250px')
)

# Create a preview button for the custom function
update_function_button = widgets.Button(
    description="Update Chart",
    disabled=False,
    layout=widgets.Layout(width='150px')
)
update_function_button_id = f'update-function-button-{id(update_function_button)}'
update_function_button.add_class(update_function_button_id)

# Function to validate and parse custom function
# Function to validate and parse custom function
def parse_custom_function(func_str):
    """
    Validates and parses a custom damage function string into a callable function.
    
    Args:
        func_str (str): Function string like "Y = 0.1*X" or "Y = 1-exp(-0.1*X)"
        
    Returns:
        callable: A function that can be applied to hazard values
    """
    # Import numpy at the function level to ensure it's available
    import numpy as np
    
    # If no function provided, return None
    if not func_str:
        return None
        
    # Replace 'Y =' or 'y =' with nothing to get just the expression
    func_str = re.sub(r'^[Yy]\s*=\s*', '', func_str)
    
    try:
        # Use sympy to parse and validate the expression
        x = symbols('X')
        expr = sympify(func_str.replace('X', 'x'))
        
        # Create a vectorized function for better performance
        def custom_func(X, wb_region=None):
            """
            IMPROVEMENT #2: Vectorized damage function
            
            Args:
                X: Hazard values (can be scalar, array, or xarray)
                wb_region: World Bank region (unused in custom functions but needed for interface compatibility)
                
            Returns:
                Damage values between 0 and 1
            """
            # Import numpy here to ensure it's available in the function scope
            import numpy as np
            
            try:
                # Handle numpy arrays directly
                if isinstance(X, np.ndarray):
                    # Create a copy to avoid modifying the input
                    result = np.zeros_like(X, dtype=np.float32)
                    # Only process valid values (non-NaN)
                    valid_mask = ~np.isnan(X)
                    
                    if not np.any(valid_mask):
                        return result  # Return zeros if no valid values
                    
                    # Extract valid values for processing
                    valid_values = X[valid_mask]
                    
                    # Convert expression to numpy function for vectorized operation
                    # This is much faster than element-by-element processing
                    import numpy as np  # Ensure numpy is available in the expression context
                    from numpy import exp, log, sin, cos, tan, sqrt, power, maximum, minimum
                    
                    # Replace sympy expression with numpy-compatible expression
                    np_expr = str(expr).replace('x', 'valid_values')
                    np_expr = np_expr.replace('Min', 'minimum').replace('Max', 'maximum')
                    
                    # Safely evaluate the expression
                    processed_values = eval(np_expr)
                    
                    # Clip results to [0,1] range
                    processed_values = np.clip(processed_values, 0.0, 1.0)
                    
                    # Assign processed values back to result array
                    result[valid_mask] = processed_values
                    return result
                
                # Handle scalar input
                if X is None or np.isnan(X):
                    return np.nan
                
                # Evaluate expression with the input value
                val = float(expr.subs('x', float(X)))
                
                # Ensure the result is between 0 and 1
                return max(0.0, min(1.0, val))
                
            except Exception as e:
                print(f"Error in custom function: {str(e)}")
                # Return NaN on error
                if isinstance(X, np.ndarray):
                    return np.zeros_like(X)
                return np.nan
        
        return custom_func
        
    except Exception as e:
        print(f"Error parsing function: {str(e)}")
        return None

# Create container for function-specific UI elements
function_container = widgets.VBox([
    widgets.Label("Custom Vulnerability Function:"),
    custom_function_input,
    custom_function_description,
    update_function_button
], layout=widgets.Layout(display='block'))

class_container = widgets.VBox([], layout=widgets.Layout(display='none'))

# For approach = function, preview impact function
def preview_impact_func(*args):
    
    # Import numpy at the function level to ensure it's available
    import numpy as np

    with approach_box:
        clear_output(wait=True)
        
        if approach_selector.value == 'Function':
            selected_exposures = exposure_selector.value
            selected_country = country_selector.value
            
            if not selected_country:
                print("Please select a country first.")
                return
            
            # Get the ISO_A3 code for the selected country
            iso_a3 = country_dict.get(selected_country, False)
            
            # Parse the custom function formula
            func_str = custom_function_input.value
            custom_func = parse_custom_function(func_str)
            
            if not custom_func:
                print("Invalid function formula. Using default linear function.")
                # Default linear function if parsing fails
                custom_func = lambda x: np.minimum(1.0, x / 10.0)
            
            if selected_exposures:
                steps = np.arange(0, 20, 0.5)  # Extend range for better visualization
                fig, ax = plt.subplots(figsize=(4, 3))
                
                for exposure in selected_exposures:
                    # Use the parsed custom function
                    values = [custom_func(x) for x in steps]
                    
                    # Plot the function
                    ax.plot(steps, values, label=exposure)
                
                ax.grid(True)
                ax.legend()
                
                ax.set_xlabel("Hazard intensity (X)")
                ax.set_ylabel("Impact Factor (Y)")
                ax.set_ylim([0, 1.05])  # Set y-axis from 0 to just above 1
                
                plt.title(f"Custom Impact Function:\n{func_str}")
                plt.tight_layout()
                display(fig)
                plt.close(fig)
            else:
                print("Please select at least one exposure category")

# Connect update button to the preview function
update_function_button.on_click(lambda b: preview_impact_func())

# For approach = classes, define class edges
class_edges_table = widgets.VBox()

# Functions to dynamically add class edges
def create_class_row(index):
    delete_button = notebook_utils.delete_button
    row = notebook_utils.create_row_box(index, delete_button)
    delete_button.on_click(lambda b: delete_class(row))
    return row

def delete_class(row):
    if len(class_edges_table.children) > 2:  # More than one class row plus the "Add Class" button
        class_edges_table.children = [child for child in class_edges_table.children if child != row]
        # Renumber the remaining classes
        for i, child in enumerate(class_edges_table.children[:-1]):  # Exclude the "Add Class" button
            child.children[0].value = f'Class {i+1}:'
        update_delete_buttons()

def update_delete_buttons():
    for child in class_edges_table.children[:-1]:  # Exclude the "Add Class" button
        child.children[2].layout.display = 'block' if len(class_edges_table.children) > 2 else 'none'

# Define add_class_button
add_class_button = widgets.Button(description="Add Class", layout=widgets.Layout(width='150px'))
add_class_button.on_click(lambda b: add_class(b))

def add_class(button):
    new_index = len(class_edges_table.children)
    class_edges_table.children = list(class_edges_table.children[:-1]) + [create_class_row(new_index)] + [add_class_button]
    update_delete_buttons()

# Modified vulnerability approach for custom functions
def create_custom_vulnerability_approach():
    return widgets.VBox([
        widgets.Label("Vulnerability Approach:"),
        approach_selector,
        widgets.HTML("<hr style='margin: 10px 0;'>"),
        function_container,
        class_container,
        approach_box
    ])

# Function to update function/class UI based on approach selector
def update_approach_ui(*args):
    approach_box.clear_output()
    
    # Show appropriate interface based on approach
    if approach_selector.value == 'Classes':
        # Hide function container and show class container
        function_container.layout.display = 'none'
        class_container.layout.display = 'block'
        
        # If we don't have class edges table initialized yet
        if len(class_edges_table.children) == 0:
            # Add initial class rows
            class_edges_table.children = [create_class_row(i) for i in range(1, 4)]
            # Add the "Add Class" button
            class_edges_table.children += (add_class_button,)
            update_delete_buttons()
        
        # Display the class edges table
        with approach_box:
            display(class_edges_table)
    else:  # Function approach
        # Show function container and hide class container
        function_container.layout.display = 'block'
        class_container.layout.display = 'none'
        
        # For function approach, show the custom function chart
        preview_impact_func()

    # Ensure at least one class remains for Classes approach
    if approach_selector.value == 'Classes' and len(class_edges_table.children) == 1:  # Only "Add Class" button remains
        class_edges_table.children = [create_class_row(1)] + list(class_edges_table.children)
        update_delete_buttons()

approach_selector.observe(update_approach_ui, 'value')

preview_chk = notebook_utils.preview_chk

# Function to update the preview when relevant widgets change
def update_preview(*args):
    preview_impact_func()

# Observe changes in relevant widgets
country_selector.observe(update_preview, names='value')
adm_level_selector.observe(update_preview, names='value')
custom_boundaries_radio.observe(update_preview, names='value')
custom_boundaries_file.observe(update_preview, names='value')
exposure_selector.observe(update_preview, names='value')
approach_selector.observe(update_preview, names='value')

# Create components for the four sections
def create_country_boundaries(
    country_selector, adm_level_selector, custom_boundaries_radio,
    select_file_button, custom_boundaries_file,
    custom_boundaries_id_field, custom_boundaries_name_field,
    zonal_stats_selector  # Add the new parameter
):
    return widgets.VBox([
        widgets.Label("Country Boundaries:"),
        country_selector,
        adm_level_selector,
        widgets.HTML("<hr style='margin: 10px 0;'>"),
        widgets.Label("Custom Boundaries (optional):"),
        custom_boundaries_radio,
        select_file_button,
        custom_boundaries_file,
        custom_boundaries_id_field,
        custom_boundaries_name_field,
        widgets.HTML("<hr style='margin: 10px 0;'>"),
        widgets.Label("Analysis Options:"),
        zonal_stats_selector  # Add the new selector here
    ])

country_boundaries = create_country_boundaries(
    country_selector, adm_level_selector, custom_boundaries_radio,
    select_file_button, custom_boundaries_file,
    custom_boundaries_id_field, custom_boundaries_name_field,
    zonal_stats_selector  # Pass the new selector
)

# Hazard info for custom hazard
def create_custom_hazard_info():
    return widgets.VBox([
        widgets.Label("Hazard Data:"),
        widgets.HBox([hazard_file_selector, select_hazard_button]),
        hazard_name_input,
        widgets.Label("Hazard Settings:"),
        hazard_threshold_slider,
        return_period_input,
        use_multi_rp,
        multi_hazard_container,
        widgets.HTML("<hr style='margin: 10px 0;'>"),
        widgets.Label("Hazard Preview:"),
        hazard_preview
    ])

hazard_info = create_custom_hazard_info()

exposure_category = notebook_utils.create_exposure_category(
    custom_exposure_radio, custom_exposure_container
)

vulnerability_approach = create_custom_vulnerability_approach()

# Arrange the sections in tabs
tabs = widgets.Tab(layout={'width': '350px', 'height': '500px'})
tabs.children = [country_boundaries, hazard_info, exposure_category, vulnerability_approach]
tabs.set_title(0, 'Boundaries')
tabs.set_title(1, 'Hazard')
tabs.set_title(2, 'Exposure')
tabs.set_title(3, 'Vulnerability')

# Remove the colored borders from tab contents
for child in tabs.children:
    child.layout.border = None
    child.layout.padding = '5px'

# Info box
info_box = notebook_utils.info_box
info_box.add_class('info-box')

# Button to run the script
run_button = notebook_utils.run_button

# Functions to run the analysis
def validate_input():
    output.clear_output()
    
    # Check country selection
    if not country_selector.value:
        print("Error: Please select a country.")
        return False
    
    # Check hazard file
    if use_multi_rp.value:
        # Check if we have at least one valid return period and file
        valid_rp_files = False
        for child in multi_hazard_container.children[1:]:  # Skip the title
            rp_text = child.children[0]
            file_text = child.children[1]
            if rp_text.value and file_text.value and os.path.exists(file_text.value):
                valid_rp_files = True
                break
        
        if not valid_rp_files:
            print("Error: Please provide at least one valid hazard raster file with a return period.")
            return False
    else:
        if not hazard_file_selector.value or not os.path.exists(hazard_file_selector.value):
            print("Error: Please select a valid hazard raster file.")
            return False
    
    # Check hazard name
    if not hazard_name_input.value:
        print("Error: Please provide a name for the hazard.")
        return False
    
    # Check boundaries
    if custom_boundaries_radio.value == 'Custom boundaries':
        if not all([custom_boundaries_id_field.value, custom_boundaries_name_field.value]):
            print("Error: Custom boundaries ID and Name fields must be specified.")
            return False          
        if not custom_boundaries_file.value or not os.path.exists(custom_boundaries_file.value): 
            print("Error: Custom boundaries file not specified or doesn't exist.")
            return False
    elif adm_level_selector.value is None:
        print("Error: Please select an Administrative Level when working with default boundaries.")
        return False
    
    # Check approach
    if approach_selector.value == 'Classes':
        class_values = [child.children[1].value for child in class_edges_table.children[:-1]]  # Exclude "Add Class" button
        if len(class_values) > 1:
            is_seq = np.all(np.diff(class_values) > 0)
            if not is_seq:
                print(f"Error: Class thresholds must be in increasing order.")
                return False
    
    # Check custom function for Function approach
    if approach_selector.value == 'Function':
        if not custom_function_input.value:
            print("Warning: Using default function as no custom function was provided.")
        else:
            # Test if the function is valid
            custom_func = parse_custom_function(custom_function_input.value)
            if custom_func is None:
                print("Warning: Custom function formula is invalid, will use default function.")
                # Continue with warning
            else:
                # Test if the function gives reasonable outputs
                try:
                    test_val = custom_func(1.0)
                    if not (0 <= test_val <= 1):
                        print(f"Warning: Function returned {test_val} for input 1.0. Values should be between 0 and 1.")
                        # Continue with warning
                except Exception as e:
                    print(f"Warning: Error evaluating custom function: {str(e)}")
                    # Continue with warning
    
    # Check exposure
    if not exposure_selector.value:
        print("Error: Please select at least one exposure category.")
        return False
    
    # If using custom exposure, check filenames
    if custom_exposure_radio.value == 'Custom exposure':
        if not all([child.value for child in custom_exposure_container.children]):
            print("Error: Please provide filenames for all custom exposure categories.")
            return False
    
    # All checks passed
    print("Validation successful. Ready to run analysis.")
    return True

# Modified function to create a damage function based on approach
def create_damage_function(approach, hazard_type, exp_cat, iso_a3, class_edges=None, custom_func_str=None):
    """
    Creates a damage function based on the selected approach.
    
    Args:
        approach (str): Analysis approach ('Function' or 'Classes')
        hazard_type (str): Hazard type
        exp_cat (str): Exposure category
        iso_a3 (str): Country ISO-3 code
        class_edges (list): Thresholds for classes approach
        custom_func_str (str): Custom function formula
        
    Returns:
        callable: A damage function to apply to hazard values
    """
    if approach == 'Function':
        # Parse the custom function from the input field
        custom_func = parse_custom_function(custom_func_str)
        if custom_func:
            return custom_func
        else:
            # Default linear function with vectorization if parsing fails
            print("Using default linear function due to parse errors")
            def default_func(x, wb_region=None):
                if isinstance(x, np.ndarray):
                    # Vectorized operation
                    result = np.zeros_like(x, dtype=np.float32)
                    valid_mask = ~np.isnan(x)
                    result[valid_mask] = np.clip(x[valid_mask] / 10.0, 0.0, 1.0)
                    return result
                else:
                    # Scalar case
                    if np.isnan(x):
                        return np.nan
                    return min(1.0, max(0.0, x / 10.0))
            
            return default_func
    
    elif approach == 'Classes':
        # For classes approach, use vectorized implementation
        def class_function(x, wb_region=None):
            if isinstance(x, np.ndarray):
                result = np.zeros_like(x, dtype=np.float32)
                valid_mask = ~np.isnan(x)
                
                if not np.any(valid_mask):
                    return result
                
                # Apply classification to valid values
                for i, threshold in enumerate(class_edges):
                    class_mask = (x >= threshold) & valid_mask
                    result[class_mask] = (i + 1) / len(class_edges)
                
                return result
            else:
                # Handle scalar input
                if np.isnan(x):
                    return np.nan
                    
                result = 0.0
                for i, threshold in enumerate(class_edges):
                    if x >= threshold:
                        result = (i + 1) / len(class_edges)
                return result
                
        return class_function
    
    else:
        # Default vectorized function
        def default_func(x, wb_region=None):
            if isinstance(x, np.ndarray):
                result = np.zeros_like(x, dtype=np.float32)
                valid_mask = ~np.isnan(x)
                result[valid_mask] = np.minimum(1.0, x[valid_mask] / 10.0)
                return result
            else:
                if np.isnan(x):
                    return np.nan
                return min(1.0, x / 10.0)
        
        return default_func
    
def run_analysis_script(b):
    import matplotlib.pyplot as plt
    import os

    # Disable the run button while analysis is running
    run_button.disabled = True
    run_button.description = "Analysis Running..."
    
    try:
        with output:
            output.clear_output(wait=True)
            
            if not validate_input():
                run_button.disabled = False
                run_button.description = "Run Analysis"
                return 
    
            # Gather input values
            country = country_dict.get(country_selector.value, False)
            if not country:
                print("Error: Invalid country selection.")
                run_button.disabled = False
                run_button.description = "Run Analysis"
                return
            
            # Set hazard category (name) for outputs
            haz_cat = hazard_name_input.value.upper()
            
            # Other inputs
            period = '2020'  # Fixed for custom hazard
            scenario = ''    # Not applicable for custom hazard
            exp_cat_list = list(exposure_selector.value)
            exp_year = '2020'  # Fixed
            adm_level = adm_level_selector.value
            analysis_type = approach_selector.value
            min_haz_slider = hazard_threshold_slider.value
            zonal_stats_type = zonal_stats_selector.value
            
            # Get class thresholds if applicable
            class_edges = []
            if analysis_type == 'Classes':
                class_edges = [child.children[1].value for child in class_edges_table.children[:-1]]  # Exclude "Add Class" button
            
            # Determine exp_nam_list
            exp_nam_list = []
            if custom_exposure_radio.value == 'Custom exposure':
                for i, exp_cat in enumerate(exp_cat_list):
                    custom_name = custom_exposure_container.children[i].value
                    exp_nam_list.append(custom_name if custom_name else f"{country}_{exp_cat}")
            else:
                exp_nam_list = [f"{country}_{exp}" for exp in exp_cat_list]
    
            # Additional parameters
            save_check_raster = False
            n_cores = None
    
            # Look up WB_REGION
            wb_region = df.loc[df['ISO_A3'] == country, 'WB_REGION'].iloc[0]
    
            # Handle custom boundaries
            use_custom_boundaries = custom_boundaries_radio.value == 'Custom boundaries'
            
            if use_custom_boundaries:
                custom_boundaries_file_path = custom_boundaries_file.value
                custom_code_field = custom_boundaries_id_field.value
                custom_name_field = custom_boundaries_name_field.value
            else:
                custom_boundaries_file_path = None
                custom_code_field = None
                custom_name_field = None
            
            # Process hazard files
            return_periods = []
            hazard_files = {}
            
            if use_multi_rp.value:
                # Get return periods and files from multi_hazard_container
                for child in multi_hazard_container.children[1:]:  # Skip the title
                    rp_text = child.children[0]
                    file_text = child.children[1]
                    
                    if rp_text.value and file_text.value and os.path.exists(file_text.value):
                        try:
                            rp = int(rp_text.value)
                            return_periods.append(rp)
                            hazard_files[rp] = file_text.value
                        except ValueError:
                            print(f"Warning: Invalid return period '{rp_text.value}'. Must be an integer.")
                
                # Sort return periods
                return_periods.sort()
            else:
                # Single return period
                try:
                    rp = int(return_period_input.value)
                    return_periods = [rp]
                    hazard_files[rp] = hazard_file_selector.value
                except ValueError:
                    print(f"Error: Invalid return period '{return_period_input.value}'. Must be an integer.")
                    run_button.disabled = False
                    run_button.description = "Run Analysis"
                    return
            
            if not return_periods:
                print("Error: No valid return periods provided.")
                run_button.disabled = False
                run_button.description = "Run Analysis"
                return
            
            # Create a custom damage function based on the selected approach
            custom_func_str = custom_function_input.value
            custom_damage_func = create_damage_function(
                analysis_type, 
                haz_type, 
                exp_cat_list[0],  # Use first exposure for initial function
                country, 
                class_edges, 
                custom_func_str
            )
            
            start_time = time.perf_counter()
    
            print(f"Starting analysis for {iso_to_country[country]} ({country})...")
            print(f"Using custom hazard: {haz_cat}")
            print(f"Return periods: {return_periods}")
            print(f"Exposure categories: {exp_cat_list}")
            print(f"Zonal statistics method: {zonal_stats_type}")
            
            # Initialize variables
            minx, miny, maxx, maxy = float('inf'), float('inf'), float('-inf'), float('-inf')
            summary_dfs, charts, layers, colormaps = [], [], [], []
            analysis_results = {}
            
            # Prepare Excel writer
            excel_file, gpkg_file = prepare_excel_gpkg_files(country, adm_level, haz_cat, period, scenario)
    
            # Run analysis for each exposure category
            for i in range(len(exp_cat_list)):
                exp_cat = exp_cat_list[i]
                exp_nam = exp_nam_list[i]
                print(f"Running analysis for {exp_cat}...")
                
                # Run the optimized analysis
                try:
                    from custom_hazard_analysis import run_analysis_with_custom_hazard
                    
                    result_df = run_analysis_with_custom_hazard(
                        country, haz_type, haz_cat, period, scenario, 
                        return_periods, min_haz_slider,
                        exp_cat, exp_nam, exp_year, adm_level, 
                        analysis_type, class_edges, 
                        save_check_raster, n_cores, 
                        use_custom_boundaries=use_custom_boundaries,
                        custom_boundaries_file_path=custom_boundaries_file_path, 
                        custom_code_field=custom_code_field,
                        custom_name_field=custom_name_field, 
                        wb_region=wb_region,
                        hazard_files=hazard_files,
                        custom_damage_func=custom_damage_func,
                        zonal_stats_type=zonal_stats_type
                    )
                    
                    if result_df is None:
                        print("Encountered Exception! Please fix issue above.")
                        continue
                    
                    sheet_name = prepare_sheet_name(analysis_type, return_periods, exp_cat)
                                
                    saving_excel_and_gpgk_file(result_df, excel_file, sheet_name, gpkg_file, exp_cat)
        
                    # Create summary DataFrame
                    summary_df = create_summary_df(result_df, return_periods, exp_cat)
                    summary_dfs.append(summary_df)
        
                    # Update bounding box for map extent
                    bounds = result_df.total_bounds
                    minx = min(minx, bounds[0])
                    miny = min(miny, bounds[1])
                    maxx = max(maxx, bounds[2])
                    maxy = max(maxy, bounds[3])
                    
                    # Save the result dataframe for the map
                    analysis_results[exp_cat] = result_df
                    
                except Exception as e:
                    print(f"Error analyzing {exp_cat}: {str(e)}")
                    import traceback
                    traceback.print_exc()
                            
            # Combine all summary DataFrames
            if summary_dfs:
                try:
                    combined_summary = prepare_and_save_summary_df(summary_dfs, exp_cat_list, excel_file, return_file=True)
         
                    # Add custom exposure information
                    notebook_utils.write_combined_summary_to_excel(
                        excel_file, combined_summary, exp_cat_list,
                        custom_exposure_radio, custom_exposure_container
                    )
        
                    # Generate charts only for Function approach
                    if analysis_type == "Function" and preview_chk.value:
                        # Only generate EAI charts if multiple return periods were used
                        is_multi_rp = use_multi_rp.value and len(return_periods) > 1
                        
                        if is_multi_rp:
                            colors = {'POP': 'blue', 'BU': 'orange', 'AGR': 'green'}
                            title_prefix = haz_cat.title() + " "
                            charts = [notebook_utils.create_eai_chart(title_prefix, combined_summary, exp_cat, period, scenario, colors.get(exp_cat, 'purple')) 
                                    for exp_cat in exp_cat_list]
                            
                            # Export charts if requested
                            if notebook_utils.export_charts_chk.value and charts:
                                notebook_utils.export_charts(
                                    common.OUTPUT_DIR, country, haz_cat, period, scenario, charts, exp_cat_list
                                )
                        else:
                            charts = []
     
                except Exception as e:
                    print(f"Error creating summary: {str(e)}")
                    import traceback
                    traceback.print_exc()
            
            print(f"Analysis completed in {time.perf_counter() - start_time:.2f} seconds")
            print(f"Results saved to Excel file: {excel_file}")
            print(f"Results saved to GeoPackage file: {gpkg_file}")
    
            # Plot results if preview is checked and we have data
            if preview_chk.value and minx != float('inf') and analysis_results:
                try:
                    # Import required libraries
                    from ipyleaflet import GeoJSON, TileLayer, LayersControl, LegendControl, Choropleth, WidgetControl
                    import branca.colormap as cm
                    import matplotlib.pyplot as plt
                    import matplotlib.colors as mcolors
                    from io import BytesIO
                    import base64
                    from ipywidgets import HTML
                    
                    print("Creating results map...")
                    
                    # Update the map widget with analysis results
                    with map_widget:
                        map_widget.clear_output(wait=True)
                        
                        # Clear any previous analysis result layers, but keep basemaps and admin boundaries
                        result_layers = [layer for layer in m.layers if hasattr(layer, 'name') and 'Result' in layer.name]
                        legend_controls = [control for control in m.controls if isinstance(control, WidgetControl) and 
                                        hasattr(control, 'widget') and 
                                        isinstance(control.widget, HTML) and
                                        'result-legend' in control.widget.value]
                        
                        for layer in result_layers:
                            m.remove_layer(layer)
                        
                        for control in legend_controls:
                            m.remove_control(control)
                        
                        # Set map center to results
                        center_lat = (miny + maxy) / 2
                        center_lon = (minx + maxx) / 2
                        m.center = (center_lat, center_lon)
                        
                        # Create a figure for all legends
                        fig = plt.figure(figsize=(2, 4 * len(exp_cat_list)))
                        
                        # Track legend images to add
                        legend_images = []
                        
                        # Add each analysis result as a layer
                        for i, (exp_cat, result_df) in enumerate(analysis_results.items()):
                            try:
                                # Determine column to show based on analysis type and whether multiple RPs are used
                                is_multi_rp = use_multi_rp.value and len(return_periods) > 1
                                
                                if analysis_type == "Function":
                                    # For Function approach, check if EAI exists (multi-RP) or use single RP impact
                                    if is_multi_rp and f'{exp_cat}_EAI' in result_df.columns:
                                        column = f'{exp_cat}_EAI'
                                        layer_name = f"{exp_cat} Expected Annual Impact - Result"
                                        legend_title = f"{exp_cat} Expected Annual Impact"
                                    else:
                                        # Check for various possible column naming patterns
                                        potential_columns = [
                                            f'RP{return_periods[0]}_{exp_cat}_imp',
                                            f'{return_periods[0]:02d}_{exp_cat}_imp',
                                            f'{return_periods[0]}_{exp_cat}_imp',
                                            f'00_{exp_cat}_imp',
                                            f'{exp_cat}_imp'
                                        ]
                                        
                                        column = None
                                        for potential_column in potential_columns:
                                            if potential_column in result_df.columns:
                                                column = potential_column
                                                print(f"Found column: {column} for {exp_cat}")
                                                break
                                        
                                        if column:
                                            rp_text = "100" if column.startswith("00_") else str(return_periods[0])
                                            layer_name = f"{exp_cat} Impact (RP{rp_text}) - Result"
                                            legend_title = f"{exp_cat} Impact (RP{rp_text})"
                                        else:
                                            print(f"Warning: Could not find impact column for {exp_cat}")
                                            print(f"Available columns: {result_df.columns.tolist()}")
                                            continue
                                        
                                elif analysis_type == "Classes":
                                    # For Classes approach, use the exposure by class
                                    if f'RP{return_periods[0]}_{exp_cat}_C1_exp' in result_df.columns:
                                        column = f'RP{return_periods[0]}_{exp_cat}_C1_exp'
                                        layer_name = f"{exp_cat} Class 1 Exposure (RP{return_periods[0]}) - Result"
                                        legend_title = f"{exp_cat} Class 1 (RP{return_periods[0]})"
                                    else:
                                        print(f"Warning: Could not find column for {exp_cat} classes")
                                        continue
                                else:
                                    print(f"Unknown analysis approach: {analysis_type}")
                                    continue
                            
                                # Skip if column not found
                                if column not in result_df.columns:
                                    print(f"Warning: Column {column} not found in results")
                                    continue
                                
                                # Filter non-zero values for better coloring
                                non_zero = result_df[result_df[column] > 0]
                                if len(non_zero) == 0:
                                    print(f"No non-zero values for {exp_cat}")
                                    continue
                                
                                # Use quantile classification for better color distribution
                                try:
                                    # Calculate quantiles based on the data
                                    n_classes = 5  # Reduced number of classes for more stability
                                    
                                    # Check if we have enough data points for quantiles
                                    if len(non_zero) < n_classes:
                                        print(f"Not enough non-zero values for {exp_cat} to create {n_classes} classes. Using min/max instead.")
                                        breaks = np.array([non_zero[column].min(), non_zero[column].max()])
                                    else:
                                        quantiles = np.linspace(0, 1, n_classes)
                                        breaks = np.quantile(non_zero[column], quantiles)
                                        
                                        # Ensure unique breaks (sometimes quantiles can produce duplicate values with skewed data)
                                        breaks = np.unique(breaks)
                                        
                                    # If we still don't have at least 2 break points, fall back to min/max
                                    if len(breaks) < 2:
                                        print(f"Could not generate enough unique break points for {exp_cat}. Using min/max instead.")
                                        min_val = non_zero[column].min()
                                        max_val = non_zero[column].max()
                                        
                                        # If min and max are identical, create a tiny range
                                        if min_val == max_val:
                                            min_val = min_val * 0.99 if min_val != 0 else 0
                                            max_val = max_val * 1.01 if max_val != 0 else 1
                                            
                                        breaks = np.array([min_val, max_val])
                                    
                                    # Debug output
                                    print(f"Generated {len(breaks)} break points for {exp_cat}: {breaks}")
                                    
                                    # Setup a spectral color palette from blue to red
                                    colors = ['#2b83ba', '#abdda4', '#ffffbf', '#fdae61', '#d7191c']
                                    
                                    # Make sure we have at least as many colors as breaks
                                    if len(colors) < len(breaks):
                                        # Use a built-in colormap if we need more colors
                                        cmap = plt.cm.get_cmap('RdYlBu_r', len(breaks))
                                        colors = [mcolors.rgb2hex(cmap(i)) for i in range(cmap.N)]
                                    
                                    # Create the colormap with calculated breaks
                                    colormap = cm.LinearColormap(
                                        colors=colors[:len(breaks)],  # Use only as many colors as we have breaks
                                        vmin=breaks[0],
                                        vmax=breaks[-1],
                                        index=breaks  # This uses the calculated breaks for classification
                                    )
                                    
                                except Exception as e:
                                    print(f"Error in quantile calculation for {exp_cat}: {str(e)}")
                                    # Fall back to a simple linear colormap
                                    vmin = non_zero[column].min()
                                    vmax = non_zero[column].max()
                                    colormap = cm.linear.RdYlBu_r.scale(vmin, vmax)
                                    breaks = np.array([vmin, vmax])
                                    print(f"Using fallback min/max color scale: {vmin} to {vmax}")
                                
                                # Create colormap
                                if exp_cat == 'POP':
                                    cmap_name = 'RdYlBu_r'
                                elif exp_cat == 'BU':
                                    cmap_name = 'RdYlBu_r'
                                elif exp_cat == 'AGR':
                                    cmap_name = 'RdYlBu_r'
                                else:
                                    cmap_name = 'RdYlBu_r'
                                
                                # Copy the dataframe to avoid modifying the original
                                layer_data = result_df.copy()
                                
                                # Create choropleth layer
                                choropleth = Choropleth(
                                    geo_data=layer_data.__geo_interface__,
                                    choro_data={str(feat['id']): feat['properties'][column] 
                                            for feat in layer_data.__geo_interface__['features']},
                                    colormap=colormap,
                                    style={
                                        'weight': 1,
                                        'fillOpacity': 0.7,
                                        'color': 'black'
                                    },
                                    hover_style={
                                        'weight': 3,
                                        'fillOpacity': 0.8
                                    },
                                    name=layer_name
                                )
                                
                                # Add the layer to the map
                                m.add(choropleth)
                                
                                # Create a separate legend for this layer
                                ax = fig.add_axes([0.3, 0.05 + (0.95 / len(exp_cat_list)) * i, 0.2, 0.9 / len(exp_cat_list)])
                                
                                # Create the colormap using our breaks
                                cmap = plt.get_cmap(cmap_name)
                                norm = mcolors.BoundaryNorm(breaks, cmap.N)
                                
                                # Create the colorbar
                                cb = plt.colorbar(plt.cm.ScalarMappable(norm=norm, cmap=cmap), 
                                                cax=ax, orientation='vertical')
                                cb.set_label(legend_title)
                                
                                # Create a single legend image for this result
                                legend_buf = BytesIO()
                                fig_one = plt.figure(figsize=(1.5, 4))
                                ax_one = fig_one.add_axes([0.3, 0.05, 0.2, 0.9])
                                cb_one = plt.colorbar(plt.cm.ScalarMappable(norm=norm, cmap=cmap), 
                                                    cax=ax_one, orientation='vertical')
                                cb_one.set_label(legend_title)
                                fig_one.savefig(legend_buf, format='png', bbox_inches='tight', transparent=True)
                                legend_buf.seek(0)
                                plt.close(fig_one)
                                
                                # Create a data URL
                                legend_data_url = f"data:image/png;base64,{base64.b64encode(legend_buf.getvalue()).decode('utf-8')}"
                                
                                # Create a widget with the legend image
                                # Place it on the left side (not overlapping with the hazard legend)
                                legend_html = f"""
                                <div class="result-legend" style="
                                    background-color: white;
                                    padding: 5px;
                                    border-radius: 5px;
                                    box-shadow: 0 0 5px rgba(0,0,0,0.3);
                                    margin-bottom: 10px;
                                ">
                                    <img src="{legend_data_url}" style="height:200px;">
                                </div>
                                """
                                legend_widget = HTML(value=legend_html)
                                # Place impact legends on the left side (hazard legend is on the right)
                                legend_control = WidgetControl(widget=legend_widget, position='bottomleft')
                                
                                # Add the legend to the map
                                m.add_control(legend_control)
                            
                            except Exception as e:
                                print(f"Error processing layer for {exp_cat}: {str(e)}")
                                continue               
                        
                        # Close the combined figure
                        plt.close(fig)
                        
                        display(m)
                            
                        print("Results map created successfully with legends")
                    
                except Exception as e:
                    print(f"Error creating results map: {str(e)}")
                    import traceback
                    traceback.print_exc()
                
            # Display charts if available
            if charts:
                with chart_output:
                    clear_output(wait=True)
                    for chart in charts:
                        display(chart)
                        plt.close(chart)  # Close the figure after displaying
    
    except Exception as e:
        print(f"An error occurred during analysis: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        # Re-enable the run button and restore its original text
        run_button.disabled = False
        run_button.description = "Run Analysis"

run_button.on_click(run_analysis_script)

# Displaying the GUI
# Create custom header widget to avoid issues with notebook_utils.create_header_widget
def create_custom_header_widget(img_path='rdl_logo.png'):
    from base64 import b64encode
    
    # Load the logo image
    try:
        with open(img_path, "rb") as img_file:
            img_base64 = b64encode(img_file.read()).decode('utf-8')
    except:
        # Use a placeholder if image not found
        img_base64 = ""
    
    header_html = f"""
    <div style='
        background: linear-gradient(to bottom, #003366, transparent);
        padding: 20px;
        border-radius: 10px 10px 0 0;
        display: flex;
        justify-content: space-between;
        align-items: center;
        width: 100%;
        box-sizing: border-box;
        overflow: hidden;
    '>
        <div style="flex: 1; min-width: 0;">
            <h1 style='color: #FFFFFF; margin: 0; font-size: 1.5vw; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;'>RISK DATA LIBRARY</h1>
            <h2 style='color: #ff5733; margin: 10px 0; font-size: 1.2vw; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;'><b>ANALYTICAL TOOL</b></h2>
            <h4 style='color: #118AB2; margin: 0; font-size: 1vw; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;'><b>CUSTOM HAZARD ANALYSIS</b></h4>
        </div>
        <img src="data:image/png;base64,{img_base64}" style="width: 200px; max-width: 200px; height: auto; margin-left: 20px;">
    </div>
    """
    
    return widgets.HTML(value=header_html, layout=widgets.Layout(width='99%'))

# Create the header widget using our custom function
header = create_custom_header_widget()

# Footer
footer = notebook_utils.create_footer()

# Output area
output = notebook_utils.output_widget
chart_output = notebook_utils.chart_output

# Sidebar
sidebar = notebook_utils.create_sidebar(info_box, tabs, output, footer)

# Chart output area (below the map)
chart_output = notebook_utils.chart_output

# Combine map and chart output, get full ui and final layout
map_and_chart, content_layout, final_layout = notebook_utils.get_ui_components(sidebar, header, map_widget)

# JavaScript to handle hover events and update the info box
js_code = f"""
<script>
document.querySelector('.{country_selector_id}').onmouseover = function() {{
    document.querySelector('.info-box textarea').value = 'Enter the country name.';
}};
document.querySelector('.{adm_level_selector_id}').onmouseover = function() {{
    document.querySelector('.info-box textarea').value = 'Select the boundaries associated with administrative level.';
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
document.querySelector('.{hazard_file_selector_id}').onmouseover = function() {{
    document.querySelector('.info-box textarea').value = 'Enter the path to your hazard raster file in GeoTIFF format.';
}};
document.querySelector('.{hazard_name_input_id}').onmouseover = function() {{
    document.querySelector('.info-box textarea').value = 'Enter a name for this hazard (e.g., flood_depth, landslide_risk, earthquake_intensity). This will be used in output filenames.';
}};
document.querySelector('.{hazard_threshold_slider_id}').onmouseover = function() {{
    document.querySelector('.info-box textarea').value = 'Set the minimum hazard threshold, in the unit of the hazard dataset.\\nValues below this threshold will be ignored.';
}};
document.querySelector('.{return_period_input_id}').onmouseover = function() {{
    document.querySelector('.info-box textarea').value = 'Enter the return period associated with this hazard (e.g., 100 for a 1-in-100 year event).';
}};
document.querySelector('.{use_multi_rp_id}').onmouseover = function() {{
    document.querySelector('.info-box textarea').value = 'Enable this to analyze multiple return periods for probabilistic risk assessment and calculate Expected Annual Impact.';
}};
document.querySelector('.{exposure_selector_id}').onmouseover = function() {{
    document.querySelector('.info-box textarea').value = 'Select the exposure category on which the risk is calculated.\\nCtrl + click or drag mouse for multiple choices.';
}};
document.querySelector('.{custom_exposure_radio_id}').onmouseover = function() {{
    document.querySelector('.info-box textarea').value = 'Choose between default exposure data or custom exposure data provided by the user.\\n\\nDefault data sources are:\\n- Population: WorldPop 2020 (100 m)\\n- Built-up: World Settlement Footprint 2019 (100 m)\\n- Agricolture: ESA World Cover 2019 - Crop area (1 km)';
}};
document.querySelector('.{custom_exposure_textbox_id}').onmouseover = function() {{
    document.querySelector('.info-box textarea').value = 'Enter the filename (without extension) of your custom exposure data.\\n- Must be a valid .tif file using CRS:4326\\n- Must be located in the EXP folder. ';
}};
document.querySelector('.{approach_selector_id}').onmouseover = function() {{
    document.querySelector('.info-box textarea').value = 'Select the approach for risk calculation:\\n\\n- Function: Uses default impact functions\\n- Classes: Assigns exposure to hazard threshold classes\\n- Custom function: Define your own mathematical impact function';
}};
document.querySelector('.{custom_function_input_id}').onmouseover = function() {{
    document.querySelector('.info-box textarea').value = 'Enter your custom impact function using X as the hazard intensity variable and Y as the impact factor.\\n\\nExamples:\\n- Linear: Y = 0.1*X\\n- Exponential: Y = 1-exp(-0.1*X)\\n- Threshold: Y = 0 if X < 10 else min(1, (X-10)/90)';
}};
document.querySelector('.{update_function_button_id}').onmouseover = function() {{
    document.querySelector('.info-box textarea').value = 'Click to update the function chart after changing the formula.';
}};
document.querySelector('.{zonal_stats_selector_id}').onmouseover = function() {{
    document.querySelector('.info-box textarea').value = 'Select the statistic to use for zonal calculations:\\n\\n- Sum: Total sum of values in each zone (default)\\n- Mean: Average value in each zone\\n- Max: Maximum value in each zone';
}};
</script>
"""

def initialize_tool():
    from IPython.display import display, HTML
    from ipyleaflet import TileLayer
    global m, basemaps_dict

    # Display the layout and inject the JavaScript code
    display(final_layout)
    display(HTML(js_code))

    # Set up the shared ipyleaflet map
    with map_widget:
        map_widget.clear_output(wait=True)

        if m is None:
            # Create a default basemap for initial display
            osm_layer = TileLayer(
                url='https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
                name='OpenStreetMap',
                base=True,
                visible=True,
                attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            )
            
            # Create the map with the OSM layer as default
            m = Map(center=(0, 0), zoom=2, scroll_wheel_zoom=True, 
                   attribution_control=False, basemap=osm_layer)

            # Define the basemap layers directly as TileLayers
            basemap_layers = {
                # OpenStreetMap is already added as the default basemap
                "Satellite": TileLayer(
                    url='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
                    name='Satellite',
                    base=True,
                    attribution='Esri World Imagery'
                ),
                 "Dark": TileLayer(
                    url='https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png',
                    name='Dark',
                    base=True,
                    attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
                ),               
                "Topographic": TileLayer(
                    url='https://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}',
                    name='Topographic',
                    base=True,
                    attribution='Esri Topographic'
                )
            }
            
            # Store reference to basemap layers, including the default OSM layer
            basemaps_dict = {"OpenStreetMap": osm_layer}
            
            # Add each additional basemap as a separate layer
            for name, layer in basemap_layers.items():
                m.add_layer(layer)
                basemaps_dict[name] = layer
            
            # Add a custom attribution at the bottom of the map
            attribution_html = """
            <div style="background-color: rgba(255, 255, 255, 0.7); 
                        font-size: 10px; padding: 3px; text-align: right;">
                OSM | Esri | CartoDB | Developed by M. Amadio
            </div>
            """
            # Import and use ipywidgets.HTML specifically
            from ipywidgets import HTML as IPyWidgetHTML
            attribution_control = IPyWidgetHTML(value=attribution_html)
            attribution_widget = WidgetControl(widget=attribution_control, position="bottomright")
            m.add_control(attribution_widget)
            
            # Add layer control - make sure this is added AFTER all layers
            layer_control = LayersControl(position="topright")
            m.add_control(layer_control)

        display(m)

    # Initial message
    with output:
        print("Welcome to the Custom Hazard Risk Analysis Tool")
        print("1. Select a country or upload custom boundaries")
        print("2. Upload your hazard raster(s) and configure settings")
        print("3. Choose exposure categories and vulnerability approach")
        print("4. Run the analysis to generate impact assessment")
        print("\nFor help, hover over any interface element to see a description")