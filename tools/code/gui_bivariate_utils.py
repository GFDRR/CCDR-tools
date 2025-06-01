import os
import geopandas as gpd
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import folium
from folium.plugins import MiniMap, Fullscreen
import ipywidgets as widgets
from IPython.display import display, clear_output, HTML
import tkinter as tk
from tkinter import filedialog
import warnings
import common

# Suppress specific warnings
warnings.filterwarnings('ignore', category=FutureWarning)
warnings.filterwarnings('ignore', message='.*initial implementation of Parquet.*')

# Create output widgets
output = widgets.Output()
map_widget = widgets.HTML(
    value=folium.Map(location=[0,0], zoom_start=2)._repr_html_(),
    layout=widgets.Layout(width='98%', height='600px')
)
chart_output = widgets.Output(layout={'width': '98%', 'height': 'auto'})

# File selection widgets
file_path_text = widgets.Text(
    value='',
    placeholder='Enter path to GeoPackage file',
    description='File:',
    disabled=False,
    layout=widgets.Layout(width='250px')
)
file_path_text_id = f'file-path-text-{id(file_path_text)}'
file_path_text.add_class(file_path_text_id)

select_file_button = widgets.Button(
    description='Select File',
    disabled=False,
    button_style='info',
    tooltip='Click to select a GeoPackage file',
    icon='folder-open',
    layout=widgets.Layout(width='150px')
)

# Layer selection dropdown (for multi-layer GeoPackage files)
layer_selector = widgets.Dropdown(
    options=[],
    value=None,
    description='Layer:',
    disabled=True,
    layout=widgets.Layout(width='250px')
)
layer_selector_id = f'layer-selector-{id(layer_selector)}'
layer_selector.add_class(layer_selector_id)

#TODO: Merge this with run_input_check class from notebook_utils.py once it is implemented as a class
def validate_input(
    id_field_selector,
    name_field_selector,
    population_field_selector,
    poverty_field_selector,
    hazard_field_selector
):
    # Return False if any selector is None
    if (
        id_field_selector.value is None or
        name_field_selector.value is None or
        population_field_selector.value is None or
        poverty_field_selector.value is None or
        hazard_field_selector.value is None
    ):
        print("Ensure all fields are selected.")
        return False
    
    return True



# Field selection dropdowns
id_field_selector = widgets.Dropdown(
    options=[],
    value=None,
    description='ID Field:',
    disabled=True,
    layout=widgets.Layout(width='250px')
)
id_field_selector_id = f'id-field-selector-{id(id_field_selector)}'
id_field_selector.add_class(id_field_selector_id)

name_field_selector = widgets.Dropdown(
    options=[],
    value=None,
    description='Name Field:',
    disabled=True,
    layout=widgets.Layout(width='250px')
)
name_field_selector_id = f'name-field-selector-{id(name_field_selector)}'
name_field_selector.add_class(name_field_selector_id)

population_field_selector = widgets.Dropdown(
    options=[],
    value=None,
    description='Population:',
    disabled=True,
    layout=widgets.Layout(width='250px')
)
population_field_selector_id = f'population-field-selector-{id(population_field_selector)}'
population_field_selector.add_class(population_field_selector_id)

wealth_field_selector = widgets.Dropdown(
    options=[],
    value=None,
    description='Poverty:',
    disabled=True,
    layout=widgets.Layout(width='250px')
)
wealth_field_selector_id = f'wealth-field-selector-{id(wealth_field_selector)}'
wealth_field_selector.add_class(wealth_field_selector_id)

hazard_field_selector = widgets.Dropdown(
    options=[],
    value=None,
    description='Hazard:',
    disabled=True,
    layout=widgets.Layout(width='250px')
)
hazard_field_selector_id = f'hazard-field-selector-{id(hazard_field_selector)}'
hazard_field_selector.add_class(hazard_field_selector_id)

# Bivariate map settings
quantiles_selector = widgets.RadioButtons(
    options=[('3×3 (Tertiles)', 3), ('4×4 (Quartiles)', 4), ('5×5 (Quintiles)', 5)],
    value=3,
    description='Quantiles:',
    disabled=False,
    layout=widgets.Layout(width='250px')
)
quantiles_selector_id = f'quantiles-selector-{id(quantiles_selector)}'
quantiles_selector.add_class(quantiles_selector_id)

# And replace with this single combined palette selector:
bivariate_palette_selector = widgets.Dropdown(
    options=[
        ('Blue-Red', 'blue_red'),
        ('Purple-Green', 'purple_green'),
        ('Pink-Blue', 'pink_blue'),
        ('Green-Blue', 'green_blue'),
        ('Purple-Yellow', 'purple_yellow')
    ],
    value='blue_red',
    description='Palette colors:',
    disabled=False,
    layout=widgets.Layout(width='250px')
)
bivariate_palette_selector_id = f'bivariate-palette-selector-{id(bivariate_palette_selector)}'
bivariate_palette_selector.add_class(bivariate_palette_selector_id)

# RWI normalization checkbox
normalize_rwi_chk = widgets.Checkbox(
    value=True,
    description='Normalize RWI with population density',
    disabled=False,
    indent=False
)
normalize_rwi_chk_id = f'normalize-rwi-chk-{id(normalize_rwi_chk)}'
normalize_rwi_chk.add_class(normalize_rwi_chk_id)

# Max exposure slider
max_exposure_slider = widgets.FloatSlider(
    value=0.50,
    min=0.1,
    max=1.0,
    step=0.05,
    description='Max Exposure:',
    disabled=False,
    continuous_update=False,
    orientation='horizontal',
    readout=True,
    readout_format='.2f',
    layout=widgets.Layout(width='250px')
)
max_exposure_slider_id = f'max-exposure-slider-{id(max_exposure_slider)}'
max_exposure_slider.add_class(max_exposure_slider_id)

# Info box
info_box = widgets.Textarea(
    value='Hover over items for descriptions.',
    disabled=True,
    layout=widgets.Layout(width='350px', height='100px')
)
info_box.add_class('info-box')

# Preview checkbox
preview_chk = widgets.Checkbox(
    value=True,
    description='Preview Results',
    disabled=False,
    indent=False
)

# Export checkbox
export_maps_chk = widgets.Checkbox(
    value=False,
    description='Export Maps as PNG',
    disabled=False,
    indent=False
)

# Export data checkbox
export_data_chk = widgets.Checkbox(
    value=False,
    description='Export Data to GeoPackage',
    disabled=False,
    indent=False
)

# Run button
run_button = widgets.Button(
    description="Create Bivariate Map",
    tooltip='Generate the bivariate map with selected settings',
    layout=widgets.Layout(width='250px'),
    button_style='danger'
)

# Function to select file
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
        file_path_text.value = file_path
        update_layer_options(file_path)
    root.destroy()

# Function to update layer options based on selected file
def update_layer_options(file_path):
    layer_selector.options = []
    layer_selector.value = None
    layer_selector.disabled = True
    
    with output:
        clear_output()
        try:
            # Try to open the GeoPackage file and get available layers
            print(f"Reading layer information from: {file_path}")
            import fiona
            layers = fiona.listlayers(file_path)
            print(f"Available layers: {', '.join(layers)}")
            
            if layers:
                layer_selector.options = layers
                layer_selector.value = layers[0]
                layer_selector.disabled = False
                
                # Load the first layer to display preview
                update_field_selectors(file_path, layers[0])
            else:
                print("No layers found in the selected file.")
        except Exception as e:
            print(f"Error reading file: {str(e)}")
            try:
                # Try loading as a shapefile
                gdf = gpd.read_file(file_path)
                print(f"Loaded shapefile with {len(gdf)} features")
                update_field_options_from_gdf(gdf)
            except Exception as e2:
                print(f"Also failed to read as shapefile: {str(e2)}")

# Function to update field selector options when layer is selected
def update_field_selectors(file_path, layer_name):
    id_field_selector.options = []
    name_field_selector.options = []
    population_field_selector.options = []
    wealth_field_selector.options = []
    hazard_field_selector.options = []
    
    id_field_selector.disabled = True
    name_field_selector.disabled = True
    population_field_selector.disabled = True
    wealth_field_selector.disabled = True
    hazard_field_selector.disabled = True
    
    with output:
        try:
            print(f"Loading layer: {layer_name}")
            gdf = gpd.read_file(file_path, layer=layer_name)
            print(f"Loaded {len(gdf)} features")
            update_field_options_from_gdf(gdf)
        except Exception as e:
            print(f"Error loading layer: {str(e)}")

# Function to update field options from loaded GeoDataFrame
def update_field_options_from_gdf(gdf):
    # Get all columns
    columns = list(gdf.columns)
    columns_without_geometry = [col for col in columns if col.lower() != 'geometry']
    
    print(f"Available fields: {', '.join(columns_without_geometry)}")
    
    # Update field selectors
    id_field_selector.options = columns_without_geometry
    name_field_selector.options = columns_without_geometry
    population_field_selector.options = columns_without_geometry
    wealth_field_selector.options = columns_without_geometry
    hazard_field_selector.options = columns_without_geometry
    
    # Try to guess appropriate fields based on common naming patterns
    id_fields = [f for f in columns_without_geometry if any(id_name in f.lower() for id_name in ['id', 'code', 'fid', 'hasc', 'key'])]
    name_fields = [f for f in columns_without_geometry if any(name in f.lower() for name in ['name', 'nam', 'title', 'label'])]
    pop_fields = [f for f in columns_without_geometry if any(pop in f.lower() for pop in ['pop', 'population', 'people'])]
    wealth_fields = [f for f in columns_without_geometry if any(wealth in f.lower() for wealth in ['rwi', 'wealth', 'income', 'gdp', 'poverty'])]
    hazard_fields = [f for f in columns_without_geometry if any(hazard in f.lower() for hazard in ['fl', 'flood', 'hazard', 'risk', 'tc', 'storm', 'eai', 'damage'])]
    
    # Set default values if matches found
    if id_fields:
        id_field_selector.value = id_fields[0]
    if name_fields:
        name_field_selector.value = name_fields[0]
    if pop_fields:
        population_field_selector.value = pop_fields[0]
    if wealth_fields:
        wealth_field_selector.value = wealth_fields[0]
    if hazard_fields:
        hazard_field_selector.value = hazard_fields[0]
    
    # Enable selectors
    id_field_selector.disabled = False
    name_field_selector.disabled = False
    population_field_selector.disabled = False
    wealth_field_selector.disabled = False
    hazard_field_selector.disabled = False
    
    # Show map preview
    update_preview_map(gdf)

# Function to update preview map
def update_preview_map(gdf):
    try:
        # Create a simple folium map with the boundaries
        m = folium.Map()
        
        # Add boundary layer with proper transformation
        folium.GeoJson(
            gdf,
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
    except Exception as e:
        with output:
            print(f"Error updating preview map: {str(e)}")

# Function to calculate population density-weighted RWI
def calculate_weighted_rwi(gdf, pop_field, rwi_field):
    # Create a copy to avoid modifying the original
    result_gdf = gdf.copy()
   
    # Check CRS and reproject to a projected CRS if needed
    if result_gdf.crs is None:
        print("Warning: CRS is not defined. Assuming EPSG:4326 for area calculation.")
        result_gdf.set_crs(epsg=4326, inplace=True)
    
    # If using a geographic CRS (like WGS84/EPSG:4326), reproject to a suitable projected CRS
    if result_gdf.crs.is_geographic:
        print("Converting to projected CRS for accurate area calculation...")
        # Get centroid to determine appropriate UTM zone
        centroid = result_gdf.unary_union.centroid
        lon, lat = centroid.x, centroid.y
        
        # Calculate UTM zone
        utm_zone = int(1 + (lon + 180) // 6)
        epsg = 32600 + utm_zone + (0 if lat >= 0 else 100)  # North vs South hemisphere
        
        # Reproject for area calculation
        area_gdf = result_gdf.to_crs(epsg=epsg)
        # Calculate area in square kilometers
        result_gdf['area_km2'] = area_gdf.geometry.area / 10**6  # Convert from m² to km²
    else:
        # Already in projected CRS
        result_gdf['area_km2'] = result_gdf.geometry.area / 10**6  # Convert from m² to km²
    
    # Calculate population density (people per km²)
    result_gdf['pop_density'] = result_gdf[pop_field] / result_gdf['area_km2']
    
    # Calculate population density-weighted RWI
    result_gdf['rwi_x_popdens'] = result_gdf[rwi_field] * result_gdf['pop_density']
    total_weighted_rwi = result_gdf['rwi_x_popdens'].sum()
    
    # Calculate the normalized weighted RWI
    result_gdf['w_RWIxPOP'] = result_gdf['rwi_x_popdens'] / total_weighted_rwi
    
    # Scale to 0-100 for easier interpretation
    min_val = result_gdf['w_RWIxPOP'].min()
    max_val = result_gdf['w_RWIxPOP'].max()
    result_gdf['w_RWIxPOP_scaled'] = 100 * (result_gdf['w_RWIxPOP'] - min_val) / (max_val - min_val)
    
    return result_gdf

# Function to create quantile classifications
# Here's a fixed version of the classify_data function:

# Here's a completely revised approach to fix the quantile mapping problem:

def classify_data(gdf, wealth_field, hazard_field, num_quantiles, wealth_field_for_classification=None):
    """
    Classify data into quantiles for bivariate mapping.
    
    Parameters:
    -----------
    gdf : GeoDataFrame
        The geodataframe with data to classify
    wealth_field : str
        Field containing wealth/poverty data (higher = poorer)
    hazard_field : str
        Field containing hazard data
    num_quantiles : int
        Number of quantiles to create
    wealth_field_for_classification : str, optional
        Field to use for wealth classification, if different from wealth_field
        
    Returns:
    --------
    result_gdf : GeoDataFrame
        Copy of input geodataframe with added classification fields
    """
    
    # Create a copy to avoid modifying the original
    result_gdf = gdf.copy()
    
    # Determine which field to use for wealth classification
    if wealth_field_for_classification is None:
        wealth_field_for_classification = wealth_field
    
    # Get wealth values and check for pre-binned data
    wealth_values = sorted(result_gdf[wealth_field_for_classification].unique())
    unique_wealth_values = len(wealth_values)
    
    print(f"Unique wealth values: {unique_wealth_values}")
    
    # Flag for whether to use pre-binned direct mapping approach
    use_direct_mapping = False
    
    # Check if data appears to be pre-binned (small number of discrete values)
    if unique_wealth_values <= 10:  # Reasonable limit for pre-binned data
        # Check if values are all integers or integer-like floats
        if all(isinstance(v, (int, np.integer)) or 
               (isinstance(v, float) and v.is_integer()) for v in wealth_values):
            use_direct_mapping = True
            print("Detected pre-binned integer-like wealth data. Using direct mapping approach.")
    
    # Process wealth quantiles
    if use_direct_mapping:
        # Direct mapping approach for pre-binned data
        min_val = min(wealth_values)
        max_val = max(wealth_values)
        range_val = max_val - min_val
        
        # Create mapping dictionary from original values to quantiles
        wealth_mapping = {}
        for val in wealth_values:
            # Calculate relative position in range (0 to 1)
            rel_pos = (val - min_val) / range_val if range_val > 0 else 0
            # Map to quantile (0 to num_quantiles-1) using floor to ensure full range
            quantile = min(int(rel_pos * num_quantiles), num_quantiles - 1)
            wealth_mapping[val] = quantile
        
        print(f"Wealth value mapping: {wealth_mapping}")
        
        # Apply mapping to create wealth quantiles
        result_gdf['wealth_quantile'] = result_gdf[wealth_field_for_classification].map(wealth_mapping)
    else:
        # Standard quantile approach for continuous data
        try:
            result_gdf['wealth_quantile'] = pd.qcut(
                result_gdf[wealth_field_for_classification], 
                q=num_quantiles, 
                labels=False, 
                duplicates='drop'
            )
            
            # Check if we got the full range of quantiles
            if result_gdf['wealth_quantile'].max() < (num_quantiles - 1):
                print(f"Warning: Wealth quantiles only range from 0 to {result_gdf['wealth_quantile'].max()}")
                print("Using manual quantile calculation...")
                
                # Try manual quantile calculation as fallback
                wealth_values = result_gdf[wealth_field_for_classification].values
                percentiles = np.linspace(0, 100, num_quantiles+1)[1:-1]
                breaks = np.percentile(wealth_values, percentiles)
                result_gdf['wealth_quantile'] = np.digitize(wealth_values, breaks)
                
                # Ensure proper range from 0 to num_quantiles-1
                result_gdf['wealth_quantile'] = result_gdf['wealth_quantile'].clip(0, num_quantiles-1)
        except Exception as e:
            print(f"Error in wealth quantile calculation: {str(e)}")
            print("Falling back to linear mapping...")
            
            # Linear mapping from min to max as emergency fallback
            vals = result_gdf[wealth_field_for_classification].values
            min_val, max_val = vals.min(), vals.max()
            range_val = max_val - min_val
            
            if range_val > 0:
                # Create normalized values and map to quantiles
                norm_vals = (vals - min_val) / range_val
                result_gdf['wealth_quantile'] = (norm_vals * (num_quantiles - 1)).astype(int)
                result_gdf['wealth_quantile'] = result_gdf['wealth_quantile'].clip(0, num_quantiles - 1)
            else:
                # If all values are the same, assign to middle quantile
                result_gdf['wealth_quantile'] = (num_quantiles - 1) // 2
    
    # Process hazard quantiles
    try:
        # Calculate hazard quantiles
        result_gdf['hazard_quantile'] = pd.qcut(
            result_gdf[hazard_field], 
            q=num_quantiles, 
            labels=False, 
            duplicates='drop'
        )
        
        # Check if hazard quantiles are limited
        if result_gdf['hazard_quantile'].max() < (num_quantiles - 1):
            print(f"Warning: Hazard quantiles only range from 0 to {result_gdf['hazard_quantile'].max()}")
            print("Using manual hazard quantile calculation...")
            
            # Try manual quantile calculation as fallback
            hazard_values = result_gdf[hazard_field].values
            percentiles = np.linspace(0, 100, num_quantiles+1)[1:-1]
            breaks = np.percentile(hazard_values, percentiles)
            result_gdf['hazard_quantile'] = np.digitize(hazard_values, breaks)
            
            # Ensure proper range from 0 to num_quantiles-1
            result_gdf['hazard_quantile'] = result_gdf['hazard_quantile'].clip(0, num_quantiles-1)
    except Exception as e:
        print(f"Error in hazard quantile calculation: {str(e)}")
        print("Falling back to linear hazard mapping...")
        
        # Linear mapping from min to max as emergency fallback
        vals = result_gdf[hazard_field].values
        min_val, max_val = vals.min(), vals.max()
        range_val = max_val - min_val
        
        if range_val > 0:
            # Create normalized values and map to quantiles
            norm_vals = (vals - min_val) / range_val
            result_gdf['hazard_quantile'] = (norm_vals * (num_quantiles - 1)).astype(int)
            result_gdf['hazard_quantile'] = result_gdf['hazard_quantile'].clip(0, num_quantiles - 1)
        else:
            # If all values are the same, assign to middle quantile
            result_gdf['hazard_quantile'] = (num_quantiles - 1) // 2
    
    # Ensure quantile columns are integers and have no nulls
    result_gdf['wealth_quantile'] = result_gdf['wealth_quantile'].fillna(0).astype(int)
    result_gdf['hazard_quantile'] = result_gdf['hazard_quantile'].fillna(0).astype(int)
    
    # Verify quantile ranges and print diagnostics
    wealth_range = (result_gdf['wealth_quantile'].min(), result_gdf['wealth_quantile'].max())
    hazard_range = (result_gdf['hazard_quantile'].min(), result_gdf['hazard_quantile'].max())
    
    print(f"Wealth quantile range: {wealth_range}")
    print(f"Hazard quantile range: {hazard_range}")
    
    # Confirm we have the full range of quantiles for the wealth dimension
    if wealth_range[1] < (num_quantiles - 1):
        print(f"Warning: Still missing some wealth quantiles. Expected max {num_quantiles-1}, got {wealth_range[1]}")
    
    # Create combined classification
    result_gdf['bivariate_class'] = result_gdf['wealth_quantile'] * num_quantiles + result_gdf['hazard_quantile']
    
    # Calculate and print the bivariate class range
    bivariate_range = (result_gdf['bivariate_class'].min(), result_gdf['bivariate_class'].max())
    print(f"Bivariate class range: {bivariate_range}")
    expected_max = (num_quantiles - 1) * num_quantiles + (num_quantiles - 1)
    if bivariate_range[1] < expected_max:
        print(f"Warning: Bivariate class does not reach expected maximum of {expected_max}")
    
    return result_gdf

# Function to generate bivariate color scheme with maximum saturation
def create_bivariate_colormap(palette_key, num_quantiles):
    """
    Create a bivariate colormap using the Stevens palette approach.
    
    This implementation uses predefined Stevens palettes and handles
    interpolation for larger grid sizes.
    
    Parameters:
    -----------
    palette_key : str
        Key identifying which Stevens palette to use (e.g., 'blue_red')
    num_quantiles : int
        Number of quantiles for each variable (3, 4, or 5)
        
    Returns:
    --------
    bivariate_colors : numpy.ndarray
        Matrix of colors for the bivariate map
    colors_list : list
        Flattened list of colors
    """
    
    # Function to convert hex to RGB float values (0-1)
    def hex_to_rgb(hex_color):
        hex_color = hex_color.lstrip('#')
        return [int(hex_color[i:i+2], 16)/255 for i in (0, 2, 4)] + [1.0]  # R,G,B + Alpha
    
    # Define Stevens 3×3 palettes
    stevens_palettes = {
        'blue_red': {  # Blue-Red palette
            (0, 0): '#e8e8e8',  # Low hazard, Low poverty
            (0, 1): '#e4cac8',  # Low hazard, Mid poverty
            (0, 2): '#c85a5a',  # Low hazard, High poverty
            (1, 0): '#b0d5df',  # Mid hazard, Low poverty
            (1, 1): '#ad9ea5',  # Mid hazard, Mid poverty
            (1, 2): '#985356',  # Mid hazard, High poverty
            (2, 0): '#64acbe',  # High hazard, Low poverty
            (2, 1): '#627f8c',  # High hazard, Mid poverty
            (2, 2): '#574249',  # High hazard, High poverty
        },
        'purple_green': {  # Purple-Green palette
            (0, 0): '#e8e8e8',  # Low hazard, Low poverty
            (0, 1): '#d4cdd9',  # Low hazard, Mid poverty
            (0, 2): '#be64ac',  # Low hazard, High poverty
            (1, 0): '#b8d6be',  # Mid hazard, Low poverty
            (1, 1): '#a9aead',  # Mid hazard, Mid poverty
            (1, 2): '#9c6290',  # Mid hazard, High poverty
            (2, 0): '#73ae80',  # High hazard, Low poverty
            (2, 1): '#6c8b74',  # High hazard, Mid poverty
            (2, 2): '#5e5e73',  # High hazard, High poverty
        },
        'pink_blue': {  # Pink-Blue palette
            (0, 0): '#e8e8e8',  # Low hazard, Low poverty
            (0, 1): '#ace4e4',  # Low hazard, Mid poverty
            (0, 2): '#5ac8c8',  # Low hazard, High poverty
            (1, 0): '#dfb0d6',  # Mid hazard, Low poverty
            (1, 1): '#a5add3',  # Mid hazard, Mid poverty
            (1, 2): '#5698b9',  # Mid hazard, High poverty
            (2, 0): '#be64ac',  # High hazard, Low poverty
            (2, 1): '#8c62aa',  # High hazard, Mid poverty
            (2, 2): '#3b4994',  # High hazard, High poverty
        },
        'green_blue': {  # Green-Blue palette
            (0, 0): '#e8e8e8',  # Low hazard, Low poverty
            (0, 1): '#b5c0da',  # Low hazard, Mid poverty
            (0, 2): '#6c83b5',  # Low hazard, High poverty
            (1, 0): '#b8d6be',  # Mid hazard, Low poverty
            (1, 1): '#90b2b3',  # Mid hazard, Mid poverty
            (1, 2): '#567994',  # Mid hazard, High poverty
            (2, 0): '#73ae80',  # High hazard, Low poverty
            (2, 1): '#5a9178',  # High hazard, Mid poverty
            (2, 2): '#2a5a5b',  # High hazard, High poverty
        },
        'purple_yellow': {  # Purple-Yellow palette
            (0, 0): '#e8e8e8',  # Low hazard, Low poverty
            (0, 1): '#e4d9ac',  # Low hazard, Mid poverty
            (0, 2): '#c8b35a',  # Low hazard, High poverty
            (1, 0): '#cbb8d7',  # Mid hazard, Low poverty
            (1, 1): '#c8ada0',  # Mid hazard, Mid poverty
            (1, 2): '#af8e53',  # Mid hazard, High poverty
            (2, 0): '#9972af',  # High hazard, Low poverty
            (2, 1): '#976b82',  # High hazard, Mid poverty
            (2, 2): '#804d36',  # High hazard, High poverty
        }
    }
    
    # Create a 4×4 palette based on the 3×3 palette (interpolation)
    def create_4x4_palette(palette_3x3):
        palette_4x4 = {}
        
        # Define corner points from 3×3 (these stay the same)
        palette_4x4[(0, 0)] = palette_3x3[(0, 0)]  # Low-Low
        palette_4x4[(0, 3)] = palette_3x3[(0, 2)]  # Low-High
        palette_4x4[(3, 0)] = palette_3x3[(2, 0)]  # High-Low
        palette_4x4[(3, 3)] = palette_3x3[(2, 2)]  # High-High
        
        # Convert all colors to RGB floats for interpolation
        colors_rgb = {pos: hex_to_rgb(color) for pos, color in palette_3x3.items()}
        
        # Generate the 4×4 palette through bilinear interpolation
        for i in range(4):
            for j in range(4):
                # Skip already defined corners
                if (i, j) in palette_4x4:
                    continue
                
                # Map 4×4 position to 3×3 position for interpolation
                x = i / 3 * 2  # Map 0-3 to 0-2
                y = j / 3 * 2  # Map 0-3 to 0-2
                
                # Find the four surrounding points in the 3×3 grid
                x0, y0 = int(x), int(y)
                x1, y1 = min(x0 + 1, 2), min(y0 + 1, 2)
                
                # Calculate interpolation weights
                wx = x - x0
                wy = y - y0
                
                # Bilinear interpolation of RGB values
                color = [0, 0, 0, 1.0]
                for c in range(3):  # RGB channels
                    color[c] = (
                        (1-wx)*(1-wy) * colors_rgb[(x0, y0)][c] +
                        wx*(1-wy) * colors_rgb[(x1, y0)][c] +
                        (1-wx)*wy * colors_rgb[(x0, y1)][c] +
                        wx*wy * colors_rgb[(x1, y1)][c]
                    )
                
                # Convert to hex and add to palette
                hex_color = mcolors.rgb2hex(color[:3])
                palette_4x4[(i, j)] = hex_color
        
        return palette_4x4
    
    # Create a 5×5 palette (similar approach to 4×4)
    def create_5x5_palette(palette_3x3):
        palette_5x5 = {}
        
        # Define corner points
        palette_5x5[(0, 0)] = palette_3x3[(0, 0)]  # Low-Low
        palette_5x5[(0, 4)] = palette_3x3[(0, 2)]  # Low-High
        palette_5x5[(4, 0)] = palette_3x3[(2, 0)]  # High-Low
        palette_5x5[(4, 4)] = palette_3x3[(2, 2)]  # High-High
        
        # Convert all colors to RGB floats for interpolation
        colors_rgb = {pos: hex_to_rgb(color) for pos, color in palette_3x3.items()}
        
        # Generate the 5×5 palette through bilinear interpolation
        for i in range(5):
            for j in range(5):
                # Skip already defined corners
                if (i, j) in palette_5x5:
                    continue
                
                # Map 5×5 position to 3×3 position for interpolation
                x = i / 4 * 2  # Map 0-4 to 0-2
                y = j / 4 * 2  # Map 0-4 to 0-2
                
                # Find the four surrounding points in the 3×3 grid
                x0, y0 = int(x), int(y)
                x1, y1 = min(x0 + 1, 2), min(y0 + 1, 2)
                
                # Calculate interpolation weights
                wx = x - x0
                wy = y - y0
                
                # Bilinear interpolation of RGB values
                color = [0, 0, 0, 1.0]
                for c in range(3):  # RGB channels
                    color[c] = (
                        (1-wx)*(1-wy) * colors_rgb[(x0, y0)][c] +
                        wx*(1-wy) * colors_rgb[(x1, y0)][c] +
                        (1-wx)*wy * colors_rgb[(x0, y1)][c] +
                        wx*wy * colors_rgb[(x1, y1)][c]
                    )
                
                # Convert to hex and add to palette
                hex_color = mcolors.rgb2hex(color[:3])
                palette_5x5[(i, j)] = hex_color
        
        return palette_5x5
    
    # Fallback to blue_red if an invalid palette key is provided
    if palette_key not in stevens_palettes:
        palette_key = 'blue_red'
    
    # Get the appropriate base palette
    base_palette = stevens_palettes[palette_key]
    
    # Select or generate the palette for the requested number of quantiles
    match num_quantiles:
        case 3:
            palette = base_palette
        case 4:
            palette = create_4x4_palette(base_palette)
        case 5:
            palette = create_5x5_palette(base_palette)
        case _:
            # Fall back to 3×3 for any other value
            palette = base_palette
            num_quantiles = 3
    
    # Create the color matrix from the palette using list comprehension
    bivariate_colors = np.array([
        [hex_to_rgb(palette[(i, j)]) for j in range(num_quantiles)]
        for i in range(num_quantiles)
    ])

    # Create a flattened list of colors
    colors_list = [bivariate_colors[i, j, :] for i in range(num_quantiles) for j in range(num_quantiles)]
    
    return bivariate_colors, colors_list

# Also update the legend creation to reflect the new color mixing logic
def create_bivariate_legend(bivariate_colors, poverty_label, hazard_label, num_quantiles, palette_name, max_exposure):
    """
    Create a legend for the bivariate map with proper labels based on palette type.
    
    Parameters:
    -----------
    bivariate_colors : numpy.ndarray
        Matrix of colors for the bivariate map
    poverty_label : str
        Label for the poverty axis
    hazard_label : str
        Label for the hazard axis
    num_quantiles : int
        Number of quantiles used
    palette_name : str
        Name of the palette (e.g., 'blue_red')
    max_exposure : float
        Maximum exposure value for the scale
        
    Returns:
    --------
    fig : matplotlib.figure.Figure
        Figure containing the legend
    """
    # Parse the palette name to get descriptive colors for labels
    palette_parts = palette_name.split('_')
    hazard_color = palette_parts[0].capitalize() if len(palette_parts) > 0 else "Blue"
    poverty_color = palette_parts[1].capitalize() if len(palette_parts) > 1 else "Red"
    
    fig, ax = plt.subplots(figsize=(4, 4))
    
    # Remove axes
    ax.set_axis_off()
    
    # Create the legend grid - with fixed orientation
    for i in range(num_quantiles):  # i capturing hazard (rows)
        for j in range(num_quantiles):  # j capturing poverty (columns)
            # Add colored square
            ax.add_patch(
                plt.Rectangle(
                    (j, i), 1, 1, 
                    facecolor=bivariate_colors[i, j, :],
                    edgecolor='k', linewidth=0.5
                )
            )
    
    # Set labels at the middle of each axis with color information
    ax.text(num_quantiles/2, -0.7, f"{poverty_label} ({poverty_color})", ha='center', va='center', fontsize=12)
    ax.text(-1.2, num_quantiles/2, f"{hazard_label} ({hazard_color})", ha='center', va='center', rotation=90, fontsize=12)
    
    # Calculate percentage labels for fixed scale exposure
    exposure_percentages = [f"{int(x*100)}%" for x in np.linspace(0, max_exposure, num_quantiles+1)]

    # For exposure (y-axis): Add percentage labels at each level
    # Position further to the left to avoid overlap
    for i in range(num_quantiles+1):
        ax.text(-0.1, i, exposure_percentages[i], ha='right', va='center', fontsize=10)
    
    # For poverty (x-axis): Low at left, High at right
    ax.text(0, -0.3, "Low", ha='center', va='top', fontsize=10)  # Poverty low (left)
    ax.text(num_quantiles, -0.3, "High", ha='center', va='top', fontsize=10)  # Poverty high (right)
    
    # Add title with palette name
    plt.title(f"Bivariate Legend: {hazard_color}-{poverty_color}", fontsize=12)
    
    # Set axis limits with more space for labels
    ax.set_xlim(-1.5, num_quantiles + 0.2)
    ax.set_ylim(-1.2, num_quantiles + 0.2)
    
    plt.tight_layout()
    
    return fig

# Function to create a summary table figure
def create_summary_table(gdf, pop_field, wealth_field, hazard_field, bivariate_palette, num_quantiles):
    """Create a summary table with key statistics"""
    # Calculate key statistics
    stats = {
        'Total Population': f"{gdf[pop_field].sum():,.0f}",
        'Total Area': f"{gdf['area_km2'].sum():,.2f} km²",
        'Mean Population Density': f"{gdf['pop_density'].mean():,.2f} people/km²",
        'Max Population Density': f"{gdf['pop_density'].max():,.2f} people/km²",
        'Wealth Index Range': f"{gdf[wealth_field].min():.4f} to {gdf[wealth_field].max():.4f}",
        'Weighted RWI Range': f"{gdf['w_RWIxPOP_scaled'].min():.2f} to {gdf['w_RWIxPOP_scaled'].max():.2f}",
        'RWI Normalization': 'Population density-weighted' if normalize_rwi_chk.value else 'Raw values (no normalization)',
        'Relative Exposure Range': f"{gdf['relative_exposure'].min():.6f} to {gdf['relative_exposure'].max():.6f}",
        'Max Exposure Scale': f"{int(max_exposure_slider.value*100)}%",
        'Number of Features': f"{len(gdf)}",
        'Quantile Grid': f"{num_quantiles}×{num_quantiles}",
        'Bivariate Palette': f"{bivariate_palette}"
    }
    
    # Additional stats for smaller datasets
    if len(gdf) <= 50:
        # Add quantile information for better interpretation
        wealth_quantiles = [f"{q:.2f}" for q in np.percentile(gdf[wealth_field], np.linspace(0, 100, num_quantiles+1))]
        hazard_quantiles = [f"{q:.2f}" for q in np.percentile(gdf[hazard_field], np.linspace(0, 100, num_quantiles+1))]
        
        stats['Poverty Quantile Breaks'] = ", ".join(wealth_quantiles)
        stats['Exposure Quantile Breaks'] = ", ".join(hazard_quantiles)
    
    # Create figure
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.axis('tight')
    ax.axis('off')
    
    # Create table with statistics
    table_data = [[k, v] for k, v in stats.items()]
    table = ax.table(cellText=table_data, 
                     colLabels=['Statistic', 'Value'],
                     loc='center',
                     cellLoc='left',
                     colWidths=[0.4, 0.6])
    
    # Style the table
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1, 1.5)  # Adjust row height
    
    # Style header
    for (i, j), cell in table.get_celld().items():
        if i == 0:  # Header row
            cell.set_text_props(fontweight='bold')
            cell.set_facecolor('#E6E6E6')
        elif i % 2 == 0:  # Alternating row colors
            cell.set_facecolor('#F5F5F5')
    
    # Add title
    plt.title('Bivariate Analysis Summary', fontsize=12, pad=10)
    plt.tight_layout()
    
    return fig

# Function to create a folium bivariate choropleth map without title overlay
def create_bivariate_map(gdf, colors_list, id_field, name_field, num_quantiles):
    # Convert colors to hex
    hex_colors = [mcolors.to_hex(c) for c in colors_list]
    
    # Create a style function with fixed class calculation
    def style_function(feature):
        feature_id = feature['properties'][id_field]
        feature_data = gdf[gdf[id_field] == feature_id]
        
        if not feature_data.empty:
            # Get wealth and hazard quantiles
            wealth_q = feature_data['wealth_quantile'].values[0]
            hazard_q = feature_data['hazard_quantile'].values[0]
            
            # Calculate bivariate class with fixed orientation
            # hazard is the row (i), wealth is the column (j)
            bivariate_class = int(hazard_q * num_quantiles + wealth_q)
            
            color = hex_colors[bivariate_class]
            return {
                'fillColor': color,
                'color': 'black',
                'weight': 1,
                'fillOpacity': 0.7
            }
        else:
            return {
                'fillColor': '#CCCCCC',
                'color': 'black',
                'weight': 1,
                'fillOpacity': 0.5
            }
    
    # Create hover function
    def highlight_function(feature):
        return {
            'weight': 3,
            'color': '#FFFFFF',
            'fillOpacity': 0.8
        }
    
    # Create popup function with added area and density information
    html = """
        <div style="width: 220px; max-height: 220px; overflow-y: auto;">
            <h4>{name}</h4>
            <p><b>Population:</b> {pop:,.0f}</p>
            <p><b>Area:</b> {area:.2f} km²</p>
            <p><b>Population Density:</b> {pop_dens:.1f} people/km²</p>
            <p><b>RWI:</b> {rwi:.4f}</p>
            <p><b>Pop.density-weighted wealth index:</b> {w_rwi:.2f}</p>
            <p><b>Absolute Exposure:</b> {hazard:.4f}</p>
            <p><b>Relative Exposure (per capita):</b> {rel_exposure:.6f}</p>
            <p><b>Poverty quantile:</b> {wealth_q}</p>
            <p><b>Exposure quantile:</b> {hazard_q}</p>
        </div>
        """

    def popup_function(feature):
        feature_id = feature['properties'][id_field]
        feature_data = gdf[gdf[id_field] == feature_id]
        
        if not feature_data.empty:
            row = feature_data.iloc[0]
            try:
                return folium.Popup(
                    html.format(
                        name=row[name_field],
                        pop=row[population_field_selector.value],
                        area=row['area_km2'],
                        pop_dens=row['pop_density'],
                        rwi=row[wealth_field_selector.value],
                        w_rwi=row['w_RWIxPOP_scaled'],
                        hazard=row[hazard_field_selector.value],
                        rel_exposure=row['relative_exposure'],
                        wealth_q=int(row['wealth_quantile']) + 1,
                        hazard_q=int(row['hazard_quantile']) + 1
                    ),
                    max_width=350
                )
            except Exception as e:
                print(f"Error creating popup: {str(e)}")
                return folium.Popup(f"Error displaying data for {row[name_field]}", max_width=350)
        else:
            return folium.Popup("No data available", max_width=350)
    
    # Create the map
    m = folium.Map()
    
    # Add GeoJSON layer
    folium.GeoJson(
        gdf.__geo_interface__,
        name='Bivariate Map',
        style_function=style_function,
        highlight_function=highlight_function,
        tooltip=folium.GeoJsonTooltip(fields=[name_field], aliases=['Name'], sticky=True),
        popup=popup_function
    ).add_to(m)
    
    # Add the MiniMap
    MiniMap(toggle_display=True, position='bottomright').add_to(m)
    
    # Add the Fullscreen button
    Fullscreen(position='bottomleft').add_to(m)
    
    # Fit to data bounds
    m.fit_bounds(m.get_bounds())
    
    return m

def create_qgis_style(gdf, colors_list, num_quantiles, palette_name):
    """
    Create a QGIS-compatible style (QML format) for the bivariate map.
    
    Parameters:
    -----------
    gdf : GeoDataFrame
        The geodataframe with classified data
    colors_list : list
        Flattened list of colors for the bivariate map
    num_quantiles : int
        Number of quantiles used
    palette_name : str
        Name of the palette used
        
    Returns:
    --------
    qgis_style : str
        XML string containing the QGIS style (QML)
    """

    hex_colors = [mcolors.to_hex(c[:3]) for c in colors_list]
    
    # Start building the QML style
    qml = """<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis version="3.22.0-Białowieża" styleCategories="Symbology" readOnly="0">
  <renderer-v2 type="categorizedSymbol" attr="bivariate_class" forceraster="0" symbollevels="0" enableorderby="0">
    <categories>
"""
    
    # Create a category for each bivariate class
    for j in range(num_quantiles):  # j capturing poverty/wealth (columns)
        for i in range(num_quantiles):  # i capturing hazard (rows)
            # Calculate bivariate class CORRECTLY
            # In the classify_data function:
            # result_gdf['bivariate_class'] = result_gdf['wealth_quantile'] * num_quantiles + result_gdf['hazard_quantile']
            bivariate_class = j * num_quantiles + i
            
            # Get the color for this class from colors_list
            # The colors_list is constructed by flattening the bivariate_colors array
            # which is filled by iterating over i (hazard, rows) first, then j (poverty, columns)
            # So we need to convert our i,j to the correct index in colors_list
            colors_list_index = i * num_quantiles + j
            color = hex_colors[colors_list_index]
            
            # Strip the # from the color
            color_code = color.lstrip('#')
            
            # Create a category for this class with the correct descriptions
            qml += f"""      <category symbol="{bivariate_class}" value="{bivariate_class}" label="Hazard: {i+1}/{num_quantiles}, Poverty: {j+1}/{num_quantiles}"/>
"""
    
    # Continue with symbols
    qml += """    </categories>
    <symbols>
"""

    # Create a symbol for each bivariate class
    for j in range(num_quantiles):  # j capturing poverty/wealth (columns)
        for i in range(num_quantiles):  # i capturing hazard (rows)
            # Calculate bivariate class CORRECTLY
            bivariate_class = j * num_quantiles + i
            
            # Get the color from the colors_list (using the correct index)
            colors_list_index = i * num_quantiles + j
            color = hex_colors[colors_list_index]
            
            # Strip the # from the color
            color_code = color.lstrip('#')
            
            # Convert hex to RGB values (QGIS format)
            r = int(color_code[0:2], 16)
            g = int(color_code[2:4], 16)
            b = int(color_code[4:6], 16)
            
            # Create a symbol for this class
            qml += f"""      <symbol type="fill" name="{bivariate_class}" alpha="1" clip_to_extent="1" force_rhr="0">
        <data_defined_properties>
          <Option type="Map">
            <Option name="name" type="QString" value=""/>
            <Option name="properties"/>
            <Option name="type" type="QString" value="collection"/>
          </Option>
        </data_defined_properties>
        <layer locked="0" enabled="1" pass="0" class="SimpleFill">
          <Option type="Map">
            <Option name="border_width_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="color" type="QString" value="{r},{g},{b},255"/>
            <Option name="joinstyle" type="QString" value="bevel"/>
            <Option name="offset" type="QString" value="0,0"/>
            <Option name="offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="offset_unit" type="QString" value="MM"/>
            <Option name="outline_color" type="QString" value="0,0,0,255"/>
            <Option name="outline_style" type="QString" value="solid"/>
            <Option name="outline_width" type="QString" value="0.26"/>
            <Option name="outline_width_unit" type="QString" value="MM"/>
            <Option name="style" type="QString" value="solid"/>
          </Option>
          <prop k="border_width_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="color" v="{r},{g},{b},255"/>
          <prop k="joinstyle" v="bevel"/>
          <prop k="offset" v="0,0"/>
          <prop k="offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="offset_unit" v="MM"/>
          <prop k="outline_color" v="0,0,0,255"/>
          <prop k="outline_style" v="solid"/>
          <prop k="outline_width" v="0.26"/>
          <prop k="outline_width_unit" v="MM"/>
          <prop k="style" v="solid"/>
        </layer>
      </symbol>
"""
    
    # Complete the QML
    qml += """    </symbols>
    <source-symbol>
      <symbol type="fill" name="0" alpha="1" clip_to_extent="1" force_rhr="0">
        <data_defined_properties>
          <Option type="Map">
            <Option name="name" type="QString" value=""/>
            <Option name="properties"/>
            <Option name="type" type="QString" value="collection"/>
          </Option>
        </data_defined_properties>
        <layer locked="0" enabled="1" pass="0" class="SimpleFill">
          <Option type="Map">
            <Option name="border_width_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="color" type="QString" value="0,0,0,255"/>
            <Option name="joinstyle" type="QString" value="bevel"/>
            <Option name="offset" type="QString" value="0,0"/>
            <Option name="offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="offset_unit" type="QString" value="MM"/>
            <Option name="outline_color" type="QString" value="0,0,0,255"/>
            <Option name="outline_style" type="QString" value="solid"/>
            <Option name="outline_width" type="QString" value="0.26"/>
            <Option name="outline_width_unit" type="QString" value="MM"/>
            <Option name="style" type="QString" value="solid"/>
          </Option>
          <prop k="border_width_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="color" v="0,0,0,255"/>
          <prop k="joinstyle" v="bevel"/>
          <prop k="offset" v="0,0"/>
          <prop k="offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="offset_unit" v="MM"/>
          <prop k="outline_color" v="0,0,0,255"/>
          <prop k="outline_style" v="solid"/>
          <prop k="outline_width" v="0.26"/>
          <prop k="outline_width_unit" v="MM"/>
          <prop k="style" v="solid"/>
        </layer>
      </symbol>
    </source-symbol>
    <rotation/>
    <sizescale/>
  </renderer-v2>
  <blendMode>0</blendMode>
</qgis>
"""
    
    return qml

def save_geopackage_with_qgis_style(gdf, output_path, colors_list, id_field, name_field, num_quantiles, palette_name):
    """
    Save GeoDataFrame to GeoPackage with embedded QGIS styling information.
    
    Parameters:
    -----------
    gdf : GeoDataFrame
        The geodataframe with classified data
    output_path : str
        Path to save the GeoPackage file
    colors_list : list
        Flattened list of colors for the bivariate map
    id_field : str
        Field containing unique identifiers
    name_field : str
        Field containing feature names
    num_quantiles : int
        Number of quantiles used
    palette_name : str
        Name of the palette used
    """
    import os
    import sqlite3
    
    # First save the geodataframe to GeoPackage
    gdf.to_file(output_path, driver="GPKG", layer="bivariate_map")
    
    # Create the QGIS style
    qgis_style = create_qgis_style(gdf, colors_list, num_quantiles, palette_name)
    
    try:
        # Connect to the GeoPackage database (it's a SQLite database)
        conn = sqlite3.connect(output_path)
        cursor = conn.cursor()
        
        # Check if layer_styles table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='layer_styles'")
        if not cursor.fetchone():
            # Create the layer_styles table according to QGIS requirements
            cursor.execute("""
            CREATE TABLE layer_styles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                f_table_catalog TEXT,
                f_table_schema TEXT,
                f_table_name TEXT,
                f_geometry_column TEXT,
                styleName TEXT,
                styleQML TEXT,
                styleSLD TEXT,
                useAsDefault BOOLEAN,
                description TEXT,
                owner TEXT,
                ui TEXT,
                update_time DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            """)
        
        # Insert the style into the layer_styles table
        cursor.execute("""
        INSERT INTO layer_styles
        (f_table_catalog, f_table_schema, f_table_name, f_geometry_column, 
         styleName, styleQML, styleSLD, useAsDefault, description, owner)
        VALUES
        (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            '', '', 'bivariate_map', 'geometry',
            f'Bivariate_Map_{palette_name}_{num_quantiles}x{num_quantiles}',
            qgis_style, '', 1,
            f'Bivariate choropleth map using {palette_name.replace("_", "-")} palette ({num_quantiles}x{num_quantiles})',
            'CCDR_RDL_Tool'
        ))
        
        # Commit changes
        conn.commit()
        
        print(f"Successfully embedded QGIS style information in GeoPackage at {output_path}")
        
    except Exception as e:
        print(f"Error adding styling information to GeoPackage: {str(e)}")
    finally:
        if conn:
            conn.close()

def export_static_map(gdf, colors_list, output_path, num_quantiles, bivariate_palette, 
                     max_exposure, dpi=300, figsize=(10, 10), title=None):
    """
    Export a high-quality static map of the bivariate choropleth using matplotlib.
    
    Parameters:
    -----------
    gdf : GeoDataFrame
        The geodataframe with classified data
    colors_list : list
        Flattened list of colors for the bivariate map
    output_path : str
        Path to save the output PNG file
    num_quantiles : int
        Number of quantiles used
    bivariate_palette : str
        Name of the palette used
    dpi : int
        Resolution of the output image
    figsize : tuple
        Size of the figure (width, height) in inches
    title : str, optional
        Title for the map. If None, a default title is generated.
    """    
    # Close any existing plots to avoid interference
    plt.close('all')
    
    # Create a new figure for the map
    _, ax = plt.subplots(figsize=figsize)
    
    # Create a mapping from bivariate_class to color
    color_map = {}
    for j in range(num_quantiles):  # j capturing poverty (columns)
        for i in range(num_quantiles):  # i capturing hazard (rows)
            # Calculate class as used in the GeoDataFrame
            bivariate_class = j * num_quantiles + i
            
            # Get color from colors_list (with different indexing)
            color_index = i * num_quantiles + j
            color_map[bivariate_class] = colors_list[color_index][:3]  # Use only RGB
    
    # Plot each polygon with its appropriate color from the bivariate classification
    for idx, row in gdf.iterrows():
        # Get the bivariate class for this feature
        biv_class = row['bivariate_class']
        
        # Get the corresponding color
        if biv_class in color_map:
            color = color_map[biv_class]
        else:
            # Fallback if class is outside expected range
            color = [0.8, 0.8, 0.8]  # Light gray
        
        # Handle both Polygon and MultiPolygon geometries
        geom = row.geometry
        
        if geom.geom_type == 'Polygon':
            # Plot a single polygon
            xs, ys = geom.exterior.xy
            ax.fill(xs, ys, color=color, edgecolor='black', linewidth=0.5)
            
            # Also plot any interior rings (holes)
            for interior in geom.interiors:
                xs, ys = interior.xy
                ax.fill(xs, ys, color='white', edgecolor='black', linewidth=0.5)
                
        elif geom.geom_type == 'MultiPolygon':
            # Plot each polygon in the multipolygon
            for part in geom.geoms:
                # Plot the exterior
                xs, ys = part.exterior.xy
                ax.fill(xs, ys, color=color, edgecolor='black', linewidth=0.5)
                
                # Plot any interior rings (holes)
                for interior in part.interiors:
                    xs, ys = interior.xy
                    ax.fill(xs, ys, color='white', edgecolor='black', linewidth=0.5)
    
    # Remove axis ticks and labels for a clean map
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_xticklabels([])
    ax.set_yticklabels([])
    
    # Set aspect ratio to equal to avoid distortion
    ax.set_aspect('equal')
    
    # Add a title if provided
    if title:
        plt.title(title, fontsize=14, pad=20)
    else:
        # Generate a default title based on palette and grid size
        default_title = f"Bivariate Map: {bivariate_palette.replace('_', '-')} ({num_quantiles}×{num_quantiles})"
        plt.title(default_title, fontsize=14, pad=20)
    
    # Set the map extent to match the data bounds with a small buffer
    bounds = gdf.total_bounds
    buffer = (bounds[2] - bounds[0]) * 0.05  # 5% buffer
    ax.set_xlim(bounds[0] - buffer, bounds[2] + buffer)
    ax.set_ylim(bounds[1] - buffer, bounds[3] + buffer)
    
    # Save the map
    plt.tight_layout()
    plt.savefig(output_path, dpi=dpi, bbox_inches='tight')
    print(f"Exported map to {output_path}")
    
    # Create a separate figure for the legend
    plt.close('all')  # Close the map figure
    _, legend_ax = plt.subplots(figsize=(4, 4))
    legend_ax.set_axis_off()
    
    # Parse the palette name to get descriptive colors for labels
    palette_parts = bivariate_palette.split('_')
    hazard_color = palette_parts[0].capitalize() if len(palette_parts) > 0 else "Blue"
    poverty_color = palette_parts[1].capitalize() if len(palette_parts) > 1 else "Red"
    
    # Create a grid of colored squares for the legend
    for i in range(num_quantiles):  # i capturing hazard (rows)
        for j in range(num_quantiles):  # j capturing poverty (columns)
            # Get color from colors_list
            color_index = i * num_quantiles + j
            color = colors_list[color_index][:3]  # Use only RGB
            
            # Add a colored rectangle
            legend_ax.add_patch(
                plt.Rectangle(
                    (j, i), 1, 1, 
                    facecolor=color,
                    edgecolor='black',
                    linewidth=0.5
                )
            )
    
    # Add labels for the axes with proper positioning
    legend_ax.text(num_quantiles/2, -0.7, f"Poverty ({poverty_color})", ha='center', va='center', fontsize=12)
    legend_ax.text(-1.2, num_quantiles/2, f"Exposure ({hazard_color})", ha='center', va='center', rotation=90, fontsize=12)
    
    # Calculate percentage labels for fixed scale exposure
    exposure_percentages = [f"{int(x*100)}%" for x in np.linspace(0, max_exposure, num_quantiles+1)]
    
    # For exposure (y-axis): Add percentage labels at each level
    for i in range(num_quantiles+1):
        legend_ax.text(-0.1, i, exposure_percentages[i], ha='right', va='center', fontsize=10)
    
    # Add "Low" and "High" labels only for the poverty axis
    legend_ax.text(0, -0.3, "Low", ha='center', va='top', fontsize=10)  # Poverty low (left)
    legend_ax.text(num_quantiles, -0.3, "High", ha='center', va='top', fontsize=10)  # Poverty high (right)
    
    # Set limits for legend with more space for labels
    legend_ax.set_xlim(-1.5, num_quantiles + 0.2)
    legend_ax.set_ylim(-1.2, num_quantiles + 0.2)
    
    # Add a title to the legend
    legend_ax.set_title(f"Bivariate Legend: {hazard_color}-{poverty_color}", fontsize=12, pad=20)
    
    # Save the legend
    legend_path = os.path.splitext(output_path)[0] + "_legend.png"
    plt.tight_layout()
    plt.savefig(legend_path, dpi=dpi, bbox_inches='tight')
    print(f"Exported legend to {legend_path}")
    
    # Close all figures
    plt.close('all')
    
    return output_path, legend_path

# Function to run the analysis
def run_analysis(b):
    run_button.disabled = True
    run_button.description = "Creating Map..."
    
    try:
        with output:
            output.clear_output(wait=True)
                    
            if not validate_input(
                id_field_selector, name_field_selector, population_field_selector,
                wealth_field_selector, hazard_field_selector
            ):
                return

            # Get input file and parameters
            file_path = file_path_text.value
            if not file_path:
                print("Error: Please select an input file")
                run_button.disabled = False
                run_button.description = "Create Bivariate Map"
                return
            
            # Get layer name (if applicable)
            layer_name = layer_selector.value if not layer_selector.disabled else None
            
            # Check required fields
            id_field = id_field_selector.value
            name_field = name_field_selector.value
            pop_field = population_field_selector.value
            wealth_field = wealth_field_selector.value
            hazard_field = hazard_field_selector.value
            normalize_rwi = normalize_rwi_chk.value
            print(f"RWI normalization: {'Enabled' if normalize_rwi else 'Disabled'}")
            
            if not (id_field and name_field and pop_field and wealth_field and hazard_field):
                print("Error: Please select all required fields")
                run_button.disabled = False
                run_button.description = "Create Bivariate Map"
                return
            
            # Get other parameters
            num_quantiles = quantiles_selector.value
            bivariate_palette = bivariate_palette_selector.value
            
            print(f"Loading data from: {file_path}")
            if layer_name:
                print(f"Layer: {layer_name}")
                gdf = gpd.read_file(file_path, layer=layer_name)
            else:
                gdf = gpd.read_file(file_path)
            
            print(f"Loaded {len(gdf)} features")
            
            # Check for numerical data in required fields
            try:
                gdf[pop_field] = pd.to_numeric(gdf[pop_field])
                gdf[wealth_field] = pd.to_numeric(gdf[wealth_field])
                gdf[hazard_field] = pd.to_numeric(gdf[hazard_field])
            except Exception as e:
                print(f"Error converting fields to numeric: {str(e)}")
                print("Please ensure population, wealth, and hazard fields contain numerical data")
                run_button.disabled = False
                run_button.description = "Create Bivariate Map"
                return
            
            # Check for negative or zero values
            if (gdf[pop_field] <= 0).any():
                print("Warning: Some population values are zero or negative. These may cause issues in calculations.")
                
            if (gdf[wealth_field] <= 0).all():
                print("Warning: All wealth values are zero or negative. This may cause issues in wealth calculations.")
            
            if (gdf[hazard_field] <= 0).all():
                print("Warning: All hazard values are zero or negative. This may cause issues in hazard calculations.")
            
            # Ensure geometry is valid for area calculation
            print("Validating geometries...")
            invalid_geoms = ~gdf.geometry.is_valid
            if invalid_geoms.any():
                print(f"Warning: Found {invalid_geoms.sum()} invalid geometries. Attempting to fix them...")
                gdf.geometry = gdf.geometry.buffer(0)  # Standard fix for many invalid geometries
            
            # Get normalization preference
            normalize_rwi = normalize_rwi_chk.value
            print(f"RWI normalization: {'Enabled' if normalize_rwi else 'Disabled'}")

            if normalize_rwi:
                print("Calculating population density-weighted wealth index...")
                gdf = calculate_weighted_rwi(gdf, pop_field, wealth_field)
                # Use the weighted RWI for classification
                wealth_field_for_classification = 'w_RWIxPOP_scaled'
            else:
                print("Using raw wealth index values (no normalization)...")
                # Create a copy to avoid modifying the original, just as in calculate_weighted_rwi
                result_gdf = gdf.copy()
                
                # Check CRS and reproject to a projected CRS if needed
                if result_gdf.crs is None:
                    print("Warning: CRS is not defined. Assuming EPSG:4326 for area calculation.")
                    result_gdf.set_crs(epsg=4326, inplace=True)
                
                # If using a geographic CRS (like WGS84/EPSG:4326), reproject to a suitable projected CRS
                if result_gdf.crs.is_geographic:
                    print("Converting to projected CRS for accurate area calculation...")
                    # Get centroid to determine appropriate UTM zone
                    centroid = result_gdf.unary_union.centroid
                    lon, lat = centroid.x, centroid.y
                    
                    # Calculate UTM zone
                    utm_zone = int(1 + (lon + 180) // 6)
                    epsg = 32600 + utm_zone + (0 if lat >= 0 else 100)  # North vs South hemisphere
                    
                    # Reproject for area calculation
                    area_gdf = result_gdf.to_crs(epsg=epsg)
                    # Calculate area in square kilometers
                    result_gdf['area_km2'] = area_gdf.geometry.area / 10**6  # Convert from m² to km²
                else:
                    # Already in projected CRS
                    result_gdf['area_km2'] = result_gdf.geometry.area / 10**6  # Convert from m² to km²
                
                # Calculate population density (people per km²)
                result_gdf['pop_density'] = result_gdf[pop_field] / result_gdf['area_km2']
                
                # Create a copy of the wealth field for the scaled version even when not normalizing
                # This ensures consistent field names in subsequent code
                result_gdf['w_RWIxPOP'] = result_gdf[wealth_field]
                
                # Scale to 0-100 for easier interpretation
                min_val = result_gdf[wealth_field].min()
                max_val = result_gdf[wealth_field].max()
                result_gdf['w_RWIxPOP_scaled'] = 100 * (result_gdf[wealth_field] - min_val) / (max_val - min_val)
                
                # Assign back to gdf to maintain consistency with the rest of the function
                gdf = result_gdf
                
                # Use the scaled version of the original wealth field for classification
                wealth_field_for_classification = 'w_RWIxPOP_scaled'

            # Now use the classify_data function to create the quantiles
            print(f"Classifying data with {num_quantiles}×{num_quantiles} grid...")
            gdf = classify_data(gdf, wealth_field, hazard_field, num_quantiles, wealth_field_for_classification)
         
            # Print summary statistics
            print("\nSummary Statistics:")
            print(f"Total Population: {gdf[pop_field].sum():,.0f}")
            print(f"Total Area: {gdf['area_km2'].sum():,.2f} km²")
            print(f"Average Population Density: {gdf['pop_density'].mean():,.2f} people/km²")
            print(f"RWI Range: {gdf[wealth_field].min():.4f} to {gdf[wealth_field].max():.4f}")
            print(f"Weighted RWI Range: {gdf['w_RWIxPOP_scaled'].min():.2f} to {gdf['w_RWIxPOP_scaled'].max():.2f}")
            print(f"Exposure to Hazard Range: {gdf[hazard_field].min():.4f} to {gdf[hazard_field].max():.4f}\n")
            
            # Calculate relative exposure (per capita)
            print("Calculating relative Exposure to Hazard")
            gdf['relative_exposure'] = gdf[hazard_field] / gdf[pop_field]
            print(f"Relative Exposure Range: {gdf['relative_exposure'].min():.6f} to {gdf['relative_exposure'].max():.6f}\n")

            # Instead of using quantiles, use a fixed scale from 0% to max_exposure% for exposure
            print(f"Creating fixed-scale classification for exposure (0-{max_exposure_slider.value*100:.1f}%)...")
            # Calculate fixed scale breaks for exposure
            exposure_max = max_exposure_slider.value  # Get value from slider
            exposure_breaks = np.linspace(0, exposure_max, num_quantiles+1)
            exposure_percentages = [f"{int(x*100)}%" for x in exposure_breaks]
            print(f"Exposure scale breaks: {', '.join(exposure_percentages)}")

            # Create wealth quantiles normally
            try:
                # Create wealth quantiles using standard method
                gdf['wealth_quantile'] = pd.qcut(
                    gdf['w_RWIxPOP_scaled'], 
                    q=num_quantiles, 
                    labels=False, 
                    duplicates='drop'
                )
            except Exception as e:
                print(f"Error in wealth quantile calculation: {str(e)}")
                print("Using manual quantile calculation...")
                wealth_values = gdf['w_RWIxPOP_scaled'].values
                gdf['wealth_quantile'] = np.digitize(
                    wealth_values,
                    np.percentile(wealth_values, np.linspace(0, 100, num_quantiles+1)[1:-1]),
                    right=True
                )

            # Manually classify exposure using fixed scale
            gdf['hazard_quantile'] = pd.cut(
                gdf['relative_exposure'], 
                bins=exposure_breaks,
                labels=False, 
                include_lowest=True
            )

            # Handle values above the max scale (40%)
            above_max = gdf['relative_exposure'] > exposure_max
            if above_max.any():
                print(f"Warning: {above_max.sum()} features have exposure above {exposure_max*100:.1f}% and are classified in the highest category")
                gdf.loc[above_max, 'hazard_quantile'] = num_quantiles - 1

            # Create combined classification
            gdf['bivariate_class'] = gdf['wealth_quantile'] * num_quantiles + gdf['hazard_quantile']

            # Generate bivariate color scheme
            print("Generating bivariate color scheme with enhanced saturation...")
            bivariate_colors, colors_list = create_bivariate_colormap(bivariate_palette, num_quantiles)

            # Create legend
            print("Creating legend...")
            legend_fig = create_bivariate_legend(bivariate_colors, "Poverty →", "Exp to Hazard →", 
                                                num_quantiles, bivariate_palette, max_exposure_slider.value)

            # Create bivariate map
            print("Creating bivariate map...")
            bivariate_map = create_bivariate_map(gdf, colors_list, id_field, name_field, num_quantiles)
            
            # Create summary table
            print("Creating summary statistics table...")
            summary_table = create_summary_table(gdf, pop_field, wealth_field, hazard_field, 
                                            bivariate_palette, num_quantiles)
            # Update the map widget with the new map
            map_widget.value = bivariate_map._repr_html_()
            
            # Display the legend and summary table side by side
            with chart_output:
                clear_output(wait=True)
                # Create two columns layout
                from ipywidgets import HBox, VBox, Output
                left_output = Output()
                right_output = Output()
                
                with left_output:
                    display(legend_fig)
                with right_output:
                    display(summary_table)
                
                display(HBox([left_output, right_output]))
            
            # Export outputs if requested
            if export_maps_chk.value:
                print("Exporting maps...")
                # Create output directory
                output_dir = os.path.join(common.OUTPUT_DIR, "bivariate_maps")
                os.makedirs(output_dir, exist_ok=True)
                
                # Save summary table
                summary_path = os.path.join(output_dir, "bivariate_summary.png")
                summary_table.savefig(summary_path, dpi=300, bbox_inches='tight')
                print(f"Saved summary table to {summary_path}")
                
                # Save interactive map as HTML
                html_map_path = os.path.join(output_dir, "bivariate_map.html")
                bivariate_map.save(html_map_path)
                print(f"Saved interactive map to {html_map_path}")
                
                # Export high-quality static map using matplotlib
                print("Generating high-quality static map with matplotlib...")
                static_map_path = os.path.join(output_dir, f"bivariate_map_{bivariate_palette}_{num_quantiles}x{num_quantiles}.png")
                try:
                    map_title = f"Bivariate Risk-Poverty Map ({bivariate_palette.replace('_', '-')} palette)"
                    map_path, legend_path = export_static_map(
                        gdf, 
                        colors_list, 
                        static_map_path, 
                        num_quantiles, 
                        bivariate_palette,
                        max_exposure_slider.value,
                        dpi=300,
                        figsize=(12, 12),
                        title=map_title
                    )
                    print("Successfully exported high-quality static maps:")
                    print(f"- Map: {map_path}")
                    print(f"- Legend: {legend_path}")
                except Exception as e:
                    import traceback
                    print(f"Error generating static map with matplotlib: {str(e)}")
                    traceback.print_exc()

            # Export data if requested
            if export_data_chk.value:
                print("Exporting data with embedded QGIS style information...")
                # Create output directory
                output_dir = os.path.join(common.OUTPUT_DIR, "bivariate_maps")
                os.makedirs(output_dir, exist_ok=True)
                
                # Create output file name with palette information
                output_file = os.path.join(output_dir, f"bivariate_map_{bivariate_palette}_{num_quantiles}x{num_quantiles}.gpkg")
                
                # Save to GeoPackage with embedded QGIS style information
                save_geopackage_with_qgis_style(
                    gdf, 
                    output_file, 
                    colors_list, 
                    id_field, 
                    name_field, 
                    num_quantiles, 
                    bivariate_palette
                )
                print(f"Saved data with embedded QGIS styling to {output_file}")
                print("This GeoPackage includes styling information for QGIS.")
                print("If the style doesn't load automatically, you can also use the separate .qml file that was created.")       
    except Exception as e:
        print(f"Error in analysis: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        run_button.disabled = False
        run_button.description = "Create Bivariate Map"

# Function to create header widget
def create_header_widget():
    header_html = """
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
            <h4 style='color: #118AB2; margin: 0; font-size: 1vw; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;'><b>BIVARIATE RISK-POVERTY MAPPING</b></h4>
        </div>
    </div>
    """
    
    return widgets.HTML(value=header_html, layout=widgets.Layout(width='99%'))

# Function to create footer
def create_footer():
    preview_container = widgets.HBox([
        preview_chk,
        export_maps_chk,
        export_data_chk
    ], layout=widgets.Layout(width='100%', justify_content='space-around'))
    
    return widgets.VBox([
        preview_container, 
        widgets.HBox([run_button], layout=widgets.Layout(display='flex', justify_content='center', width='100%'))
    ], layout=widgets.Layout(width='100%', height='100px', padding='10px'))

# Function to create sidebar
def create_sidebar(info_box, tabs, output, footer):
    sidebar_content = widgets.VBox([
        info_box,
        tabs,
        output
    ], layout=widgets.Layout(overflow='auto'))

    return widgets.VBox([
        sidebar_content,
        footer
    ], layout=widgets.Layout(width='370px', height='100%'))

# Function to create UI components
def get_ui_components(sidebar, header):
    map_and_chart = widgets.VBox(
        [map_widget, chart_output],
        layout=widgets.Layout(width='750px', height='100%')
    )
        
    content_layout = widgets.HBox(
        [sidebar, map_and_chart],
        layout=widgets.Layout(width='100%', height='800px')
    )
    
    final_layout = widgets.VBox(
        [header, content_layout],
        layout=widgets.Layout(width='100%')
    )

    return map_and_chart, content_layout, final_layout

# Function to create JavaScript code for tooltips
def create_js_code():
    return f"""
    <script>
    document.querySelector('.{file_path_text_id}').onmouseover = function() {{
        document.querySelector('.info-box textarea').value = 'Enter the path to your GeoPackage file containing boundary data with wealth and hazard information.';
    }};
    document.querySelector('.{layer_selector_id}').onmouseover = function() {{
        document.querySelector('.info-box textarea').value = 'Select the layer from the GeoPackage file to analyze. This is only applicable if your file contains multiple layers.';
    }};
    document.querySelector('.{id_field_selector_id}').onmouseover = function() {{
        document.querySelector('.info-box textarea').value = 'Select the field that contains unique identifiers for each boundary feature.';
    }};
    document.querySelector('.{name_field_selector_id}').onmouseover = function() {{
        document.querySelector('.info-box textarea').value = 'Select the field that contains the name or label for each boundary feature.';
    }};
    document.querySelector('.{population_field_selector_id}').onmouseover = function() {{
        document.querySelector('.info-box textarea').value = 'Select the field that contains population data. This is used to calculate population-weighted wealth index.';
    }};
    document.querySelector('.{wealth_field_selector_id}').onmouseover = function() {{
        document.querySelector('.info-box textarea').value = 'Select the field that contains relative wealth index (RWI) or other wealth indicator data.';
    }};
    document.querySelector('.{hazard_field_selector_id}').onmouseover = function() {{
        document.querySelector('.info-box textarea').value = 'Select the field that contains hazard risk data (e.g., flood risk index, expected annual impact).';
    }};
    document.querySelector('.{quantiles_selector_id}').onmouseover = function() {{
        document.querySelector('.info-box textarea').value = 'Select the number of quantiles to use for classifying both wealth and hazard data.\\n\\n3×3 creates a 9-cell bivariate map (tertiles)\\n4×4 creates a 16-cell bivariate map (quartiles)\\n5×5 creates a 25-cell bivariate map (quintiles)';
    }};
    document.querySelector('.{bivariate_palette_selector_id}').onmouseover = function() {{
        document.querySelector('.info-box textarea').value = 'Select the bivariate color palette to use for the map. Each palette is designed to show both poverty and hazard risk with appropriate color relationships.';
    }};
    document.querySelector('.{normalize_rwi_chk_id}').onmouseover = function() {{
    document.querySelector('.info-box textarea').value = 'Toggle whether to normalize the wealth index by population density. When enabled, areas with higher population density will have more weight in the wealth classification.';
    }};
    document.querySelector('.{max_exposure_slider_id}').onmouseover = function() {{
    document.querySelector('.info-box textarea').value = 'Set the maximum exposure value for the hazard classification scale. This defines the upper limit for the hazard dimension in the bivariate map.';
    }};
    </script>
    """

# Function to create tabs for the UI
def create_tabs():
    
    HTML_STYLE = "<hr style='margin: 10px 0;'>"
    # Create data tab
    data_tab = widgets.VBox([
        widgets.Label("Input Data:"),
        widgets.HBox([file_path_text, select_file_button]),
        layer_selector,
        widgets.HTML(HTML_STYLE),
        widgets.Label("Field Selection:"),
        id_field_selector,
        name_field_selector,
        population_field_selector,
        wealth_field_selector,
        hazard_field_selector,
    ], layout=widgets.Layout(padding='10px'))
    
    # Create bivariate mapping tab
    bivariate_tab = widgets.VBox([
        widgets.Label("Bivariate Map Settings:"),
        quantiles_selector,
        widgets.HTML(HTML_STYLE),
        widgets.Label("Color Palettes:"),
        bivariate_palette_selector,
        widgets.HTML(HTML_STYLE),
        widgets.Label("Analysis Options:"),
        max_exposure_slider,
        normalize_rwi_chk,
    ], layout=widgets.Layout(padding='10px'))
    
    # Create tabs
    tabs = widgets.Tab(layout={'width': '350px', 'height': '500px'})
    tabs.children = [data_tab, bivariate_tab]
    tabs.set_title(0, 'Data')
    tabs.set_title(1, 'Bivariate Map')
    
    return tabs

# Function to initialize the tool
def initialize_tool():
    # Connect event handlers
    select_file_button.on_click(select_file)
    run_button.on_click(run_analysis)
    
    # Create header
    header = create_header_widget()
    
    # Create tabs
    tabs = create_tabs()
    
    # Create footer
    footer = create_footer()
    
    # Create sidebar
    sidebar = create_sidebar(info_box, tabs, output, footer)
    
    # Combine components to create final layout
    _, _, final_layout = get_ui_components(sidebar, header)
    
    # Display the layout
    display(final_layout)
    
    # Add JavaScript for tooltips
    display(HTML(create_js_code()))
    
    # Initialize empty map
    m = folium.Map(location=[0, 0], zoom_start=2)
    map_widget.value = m._repr_html_()
    
    # Print welcome message
    with output:
        print("Welcome to the Bivariate Risk-Poverty Mapping Tool")
        print("1. Select a GeoPackage file with boundary data")
        print("2. Choose fields for ID, Name, Population, RWI, and Hazard risk")
        print("3. Select bivariate map settings (quantiles and color palettes)")
        print("4. Click 'Create Bivariate Map' to generate the visualization")
        print("\nResults will include:")
        print("- Interactive map with data exploration capabilities")
        print("- Color legend showing the bivariate classification")
        print("- Summary statistics table for additional context")