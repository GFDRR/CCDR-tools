import os
import geopandas as gpd
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.patches import Patch
from matplotlib.colors import ListedColormap
from matplotlib.colors import LinearSegmentedColormap
import folium
from folium.plugins import MiniMap, Fullscreen
import ipywidgets as widgets
from IPython.display import display, clear_output, HTML
import tkinter as tk
from tkinter import filedialog
import warnings
import common
import fiona

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

wealth_palette_selector = widgets.Dropdown(
    options=[
        ('Teal', '#e8e8e8, #5ac8c8'),
        ('Red', '#e8e8e8, #c85a5a'),
        ('Blue', '#e8e8e8, #6c83b5'),
        ('Oranges', 'Oranges')
    ],
    value='#e8e8e8, #5ac8c8',
    description='Poverty Palette:',
    disabled=False,
    layout=widgets.Layout(width='250px')
)
wealth_palette_selector_id = f'wealth-palette-selector-{id(wealth_palette_selector)}'
wealth_palette_selector.add_class(wealth_palette_selector_id)

hazard_palette_selector = widgets.Dropdown(
    options=[
        ('Purple', '#e8e8e8, #be64ac'),
        ('Blue', '#e8e8e8, #64acbe'),
        ('Green', '#e8e8e8, #73ae80'),
        ('Oranges', 'Oranges')
    ],
    value='#e8e8e8, #be64ac',
    description='Hazard Palette:',
    disabled=False,
    layout=widgets.Layout(width='250px')
)
hazard_palette_selector_id = f'hazard-palette-selector-{id(hazard_palette_selector)}'
hazard_palette_selector.add_class(hazard_palette_selector_id)

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
def classify_data(gdf, wealth_field, hazard_field, num_quantiles):
    # Create a copy to avoid modifying the original
    result_gdf = gdf.copy()
    
    # For "poverty" we invert the wealth index by using -1 * values
    # This makes higher quantiles = higher poverty (lower RWI)
    result_gdf[f'wealth_quantile'] = pd.qcut(
        -1 * result_gdf[wealth_field],  # Negate the values to invert them
        q=num_quantiles, 
        labels=False, 
        duplicates='drop'
    )
    
    result_gdf[f'hazard_quantile'] = pd.qcut(
        result_gdf[hazard_field], 
        q=num_quantiles, 
        labels=False, 
        duplicates='drop'
    )
    
    # Create combined classification
    result_gdf['bivariate_class'] = result_gdf['wealth_quantile'] * num_quantiles + result_gdf['hazard_quantile']
    
    return result_gdf

# Function to generate bivariate color scheme with maximum saturation
def create_bivariate_colormap(poverty_cmap, hazard_cmap, num_quantiles):
    """
    Create a bivariate colormap using specified poverty and hazard colormaps.
    Considers quantile values when mixing colors to determine relative importance.
    
    Parameters:
    -----------
    poverty_cmap : str
        Name of poverty colormap or comma-separated color gradient (start, end)
    hazard_cmap : str
        Name of hazard colormap or comma-separated color gradient (start, end)
    num_quantiles : int
        Number of quantiles for each variable
        
    Returns:
    --------
    bivariate_colors : numpy.ndarray
        Matrix of colors for the bivariate map
    colors_list : list
        Flattened list of colors
    """
    # Check if using custom gradient format: "color1, color2"
    def create_cmap_from_gradient(cmap_spec):
        if ',' in cmap_spec:
            # Parse start and end colors from the comma-separated string
            colors = [c.strip() for c in cmap_spec.split(',')]
            if len(colors) >= 2:
                return LinearSegmentedColormap.from_list('custom', colors, N=256)
        # Return the original colormap name if not a custom gradient
        return plt.cm.get_cmap(cmap_spec)
    
    # Get the appropriate colormaps
    poverty_cm = create_cmap_from_gradient(poverty_cmap)
    hazard_cm = create_cmap_from_gradient(hazard_cmap)
    
    # Generate color arrays using evenly spaced points for better contrast
    poverty_colors = poverty_cm(np.linspace(0.0, 1.0, num_quantiles))
    hazard_colors = hazard_cm(np.linspace(0.0, 1.0, num_quantiles))
    
    # Create empty matrix to store colors
    bivariate_colors = np.zeros((num_quantiles, num_quantiles, 4))
    
    # Fill the matrix with blended colors
    # poverty on x-axis (columns), hazard on y-axis (rows)
    for i in range(num_quantiles):  # i = hazard (rows)
        for j in range(num_quantiles):  # j = poverty (columns)
            # Get the base colors
            hazard_color = hazard_colors[i, :]
            poverty_color = poverty_colors[j, :]
            
            # Calculate the quantile-weighted importance
            # Higher quantiles get more weight to emphasize high-high combinations
            hazard_weight = (i + 1) / num_quantiles
            poverty_weight = (j + 1) / num_quantiles
            
            # Normalize weights to ensure they sum to 1
            total_weight = hazard_weight + poverty_weight
            hazard_weight = hazard_weight / total_weight
            poverty_weight = poverty_weight / total_weight
            
            # Calculate blended color with weighted importance
            blended = hazard_color * hazard_weight + poverty_color * poverty_weight
            
            # Enhance color saturation and contrast
            rgb = blended[:3]  # Just the RGB components, not alpha
            min_val = min(rgb)
            max_val = max(rgb)
            
            if max_val > min_val:  # Avoid division by zero
                # Apply saturation enhancement
                saturation_boost = 1.3
                
                for c in range(3):  # RGB channels
                    # Normalize to [0,1]
                    normalized = (rgb[c] - min_val) / (max_val - min_val)
                    
                    # Apply power curve for saturation boost
                    boosted = min_val + (normalized ** (1/saturation_boost)) * (max_val - min_val)
                    
                    # Clamp to valid range
                    blended[c] = max(0.0, min(1.0, boosted))
            
            bivariate_colors[i, j, :] = blended
    
    # Create a flattened list of colors
    colors_list = []
    for i in range(num_quantiles):
        for j in range(num_quantiles):
            colors_list.append(bivariate_colors[i, j, :])
    
    return bivariate_colors, colors_list

# Also update the legend creation to reflect the new color mixing logic
def create_bivariate_legend(bivariate_colors, poverty_label, hazard_label, num_quantiles):
    fig, ax = plt.subplots(figsize=(4, 4))
    
    # Remove axes
    ax.set_axis_off()
    
    # Create the legend grid - with fixed orientation
    for i in range(num_quantiles):  # i = hazard (rows)
        for j in range(num_quantiles):  # j = poverty (columns)
            # Add colored square
            ax.add_patch(
                plt.Rectangle(
                    (j, i), 1, 1, 
                    facecolor=bivariate_colors[i, j, :],
                    edgecolor='k', linewidth=0.5
                )
            )
    
    # Set labels at the middle of each axis
    ax.text(num_quantiles/2, -0.7, poverty_label, ha='center', va='center', fontsize=12)
    ax.text(-0.7, num_quantiles/2, hazard_label, ha='center', va='center', rotation=90, fontsize=12)
    
    # Adjust "Low" and "High" positions for both axes to put "High" at the end
    # For hazard (y-axis): Low at bottom, High at top
    ax.text(-0.3, 0, "Low", ha='right', va='center', fontsize=10)  # Hazard low (bottom)
    ax.text(-0.3, num_quantiles, "High", ha='right', va='center', fontsize=10)  # Hazard high (top)
    
    # For poverty (x-axis): Low at left, High at right
    ax.text(0, -0.3, "Low", ha='center', va='top', fontsize=10)  # Poverty low (left)
    ax.text(num_quantiles, -0.3, "High", ha='center', va='top', fontsize=10)  # Poverty high (right)
    
    # Set axis limits with more space for labels
    ax.set_xlim(-1.2, num_quantiles + 0.2)
    ax.set_ylim(-1.2, num_quantiles + 0.2)
    
    plt.tight_layout()
    
    return fig

# Function to create a summary table figure
def create_summary_table(gdf, pop_field, wealth_field, hazard_field, wealth_palette, hazard_palette, num_quantiles):
    """Create a summary table with key statistics"""
    # Calculate key statistics
    stats = {
        'Total Population': f"{gdf[pop_field].sum():,.0f}",
        'Total Area': f"{gdf['area_km2'].sum():,.2f} km²",
        'Mean Population Density': f"{gdf['pop_density'].mean():,.2f} people/km²",
        'Max Population Density': f"{gdf['pop_density'].max():,.2f} people/km²",
        'Wealth Index Range': f"{gdf[wealth_field].min():.4f} to {gdf[wealth_field].max():.4f}",
        'Weighted RWI Range': f"{gdf['w_RWIxPOP_scaled'].min():.2f} to {gdf['w_RWIxPOP_scaled'].max():.2f}",
        'Hazard Value Range': f"{gdf[hazard_field].min():.4f} to {gdf[hazard_field].max():.4f}",
        'Number of Features': f"{len(gdf)}",
        'Quantile Grid': f"{num_quantiles}×{num_quantiles}",
        'Poverty Palette': f"{wealth_palette}",
        'Hazard Palette': f"{hazard_palette}"
    }
    
    # Additional stats for smaller datasets
    if len(gdf) <= 50:
        # Add quantile information for better interpretation
        wealth_quantiles = [f"{q:.2f}" for q in np.percentile(gdf[wealth_field], np.linspace(0, 100, num_quantiles+1))]
        hazard_quantiles = [f"{q:.2f}" for q in np.percentile(gdf[hazard_field], np.linspace(0, 100, num_quantiles+1))]
        
        stats['Poverty Quantile Breaks'] = ", ".join(wealth_quantiles)
        stats['Hazard Quantile Breaks'] = ", ".join(hazard_quantiles)
    
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
def create_bivariate_map(gdf, colors_list, id_field, name_field, num_quantiles, title):
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
        <p><b>Hazard value:</b> {hazard:.4f}</p>
        <p><b>Poverty quantile:</b> {wealth_q}</p>
        <p><b>Hazard quantile:</b> {hazard_q}</p>
    </div>
    """
    
    def popup_function(feature):
        feature_id = feature['properties'][id_field]
        feature_data = gdf[gdf[id_field] == feature_id]
        
        if not feature_data.empty:
            row = feature_data.iloc[0]
            return folium.Popup(
                html.format(
                    name=row[name_field],
                    pop=row[population_field_selector.value],
                    area=row['area_km2'],
                    pop_dens=row['pop_density'],
                    rwi=row[wealth_field_selector.value],
                    w_rwi=row['w_RWIxPOP_scaled'],
                    hazard=row[hazard_field_selector.value],
                    wealth_q=int(row['wealth_quantile']) + 1,
                    hazard_q=int(row['hazard_quantile']) + 1
                ),
                max_width=350
            )
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

# Function to run the analysis
def run_analysis(b):
    run_button.disabled = True
    run_button.description = "Creating Map..."
    
    with output:
        output.clear_output(wait=True)
        
        try:
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
            
            if not (id_field and name_field and pop_field and wealth_field and hazard_field):
                print("Error: Please select all required fields")
                run_button.disabled = False
                run_button.description = "Create Bivariate Map"
                return
            
            # Get other parameters
            num_quantiles = quantiles_selector.value
            wealth_palette = wealth_palette_selector.value
            hazard_palette = hazard_palette_selector.value
            
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
            
            # Calculate population density-weighted RWI
            print("Calculating population density-weighted wealth index...")
            gdf = calculate_weighted_rwi(gdf, pop_field, wealth_field)
            
            # Print summary statistics
            print(f"\nSummary Statistics:")
            print(f"Total Population: {gdf[pop_field].sum():,.0f}")
            print(f"Total Area: {gdf['area_km2'].sum():,.2f} km²")
            print(f"Average Population Density: {gdf['pop_density'].mean():,.2f} people/km²")
            print(f"RWI Range: {gdf[wealth_field].min():.4f} to {gdf[wealth_field].max():.4f}")
            print(f"Weighted RWI Range: {gdf['w_RWIxPOP_scaled'].min():.2f} to {gdf['w_RWIxPOP_scaled'].max():.2f}")
            print(f"Hazard Range: {gdf[hazard_field].min():.4f} to {gdf[hazard_field].max():.4f}\n")
            
            # Create quantile classifications
            print(f"Creating {num_quantiles}×{num_quantiles} quantile classifications...")
            gdf = classify_data(gdf, 'w_RWIxPOP_scaled', hazard_field, num_quantiles)
            
            # Generate bivariate color scheme
            print("Generating bivariate color scheme with enhanced saturation...")
            bivariate_colors, colors_list = create_bivariate_colormap(wealth_palette, hazard_palette, num_quantiles)
            
            # Create legend
            print("Creating legend...")
            legend_fig = create_bivariate_legend(bivariate_colors, "Poverty →", "Hazard →", num_quantiles)
            
            # Create bivariate map
            print("Creating bivariate map...")
            title = f"Bivariate Map: Poverty ({wealth_palette}) × Hazard ({hazard_palette})"
            bivariate_map = create_bivariate_map(gdf, colors_list, id_field, name_field, num_quantiles, title)
            
            # Create summary table
            print("Creating summary statistics table...")
            summary_table = create_summary_table(gdf, pop_field, wealth_field, hazard_field, 
                                               wealth_palette, hazard_palette, num_quantiles)
            
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
                
                # Save legend
                legend_path = os.path.join(output_dir, f"bivariate_legend_{num_quantiles}x{num_quantiles}.png")
                legend_fig.savefig(legend_path, dpi=300, bbox_inches='tight')
                print(f"Saved legend to {legend_path}")
                
                # Save summary table
                summary_path = os.path.join(output_dir, f"bivariate_summary.png")
                summary_table.savefig(summary_path, dpi=300, bbox_inches='tight')
                print(f"Saved summary table to {summary_path}")
                
                # Save interactive map as HTML
                map_path = os.path.join(output_dir, f"bivariate_map.html")
                bivariate_map.save(map_path)
                print(f"Saved interactive map to {map_path}")
                
                # Save static map as PNG (optional)
                try:
                    import selenium
                    from selenium import webdriver
                    import time
                    
                    print("Generating static map image...")
                    
                    # Set up headless browser
                    options = webdriver.ChromeOptions()
                    options.add_argument('--headless')
                    driver = webdriver.Chrome(options=options)
                    
                    # Load the HTML file
                    driver.get(f"file://{os.path.abspath(map_path)}")
                    
                    # Wait for the map to load
                    time.sleep(3)
                    
                    # Take a screenshot
                    png_path = os.path.join(output_dir, f"bivariate_map.png")
                    driver.save_screenshot(png_path)
                    driver.quit()
                    
                    print(f"Saved static map image to {png_path}")
                except ImportError:
                    print("Note: Selenium not available for static image export. Install selenium package for this feature.")
                except Exception as e:
                    print(f"Error generating static map image: {str(e)}")
            
            # Export data if requested
            if export_data_chk.value:
                print("Exporting data...")
                # Create output directory
                output_dir = os.path.join(common.OUTPUT_DIR, "bivariate_maps")
                os.makedirs(output_dir, exist_ok=True)
                
                # Create output file name
                output_file = os.path.join(output_dir, f"bivariate_data.gpkg")
                
                # Save to GeoPackage
                gdf.to_file(output_file, driver="GPKG")
                print(f"Saved data to {output_file}")
            
            print("Analysis completed successfully")
            
        except Exception as e:
            print(f"Error in analysis: {str(e)}")
            import traceback
            traceback.print_exc()
        
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
    document.querySelector('.{wealth_palette_selector_id}').onmouseover = function() {{
        document.querySelector('.info-box textarea').value = 'Select the color palette to use for representing poverty in the bivariate map.';
    }};
    document.querySelector('.{hazard_palette_selector_id}').onmouseover = function() {{
        document.querySelector('.info-box textarea').value = 'Select the color palette to use for representing hazard in the bivariate map.';
    }};
    </script>
    """

# Function to create tabs for the UI
def create_tabs():
    # Create data tab
    data_tab = widgets.VBox([
        widgets.Label("Input Data:"),
        widgets.HBox([file_path_text, select_file_button]),
        layer_selector,
        widgets.HTML("<hr style='margin: 10px 0;'>"),
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
        widgets.HTML("<hr style='margin: 10px 0;'>"),
        widgets.Label("Color Palettes:"),
        wealth_palette_selector,
        hazard_palette_selector,
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
    map_and_chart, content_layout, final_layout = get_ui_components(sidebar, header)
    
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