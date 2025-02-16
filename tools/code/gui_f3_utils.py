import common
import folium
from folium.plugins import MiniMap, Fullscreen
import geopandas as gpd
from IPython.display import display, clear_output, HTML
import ipywidgets as widgets
import matplotlib.pyplot as plt
from matplotlib.ticker import StrMethodFormatter
import numpy as np
import pandas as pd
import requests
import seaborn as sns
import time
import tkinter as tk
from tkinter import filedialog

from damageFunctions import FL_mortality_factor, FL_damage_factor_builtup, FL_damage_factor_agri
from input_utils import get_adm_data
import notebook_utils
from runAnalysis import (
    run_analysis, plot_results, create_summary_df, prepare_excel_gpkg_files,
    prepare_sheet_name, saving_excel_and_gpgk_file, prepare_and_save_summary_df
)

# Define hazard type
haz_type = 'FL'

# Load country data
df = pd.read_csv('countries.csv')
country_dict = dict(zip(df['NAM_0'], df['ISO_A3']))
iso_to_country = dict(zip(df['ISO_A3'], df['NAM_0']))

# Create the Combobox widget with auto-complete functionality
country_selector = widgets.Combobox(
    placeholder='Type country name...',
    options=list(country_dict.keys()),  # Available country options
    layout=widgets.Layout(width='250px'),
    ensure_option=True,  # Ensure that only valid options can be selected
)

country_selector_id = f'country-selector-{id(country_selector)}'
country_selector.add_class(country_selector_id)

# Define a function to handle changes in the combobox
def on_country_change(change):
    with output:
        output.clear_output()
        selected_country = change['new']

        iso_a3 = country_dict[selected_country]
        print(f'Selected Country: {selected_country}, ISO_A3 Code: {iso_a3}')
        
        # Reset ADM level selector
        adm_level_selector.value = None
        
        # Fetch and display country boundaries
        try:
            gdf = get_adm_data(iso_a3, 0)
            plot_geospatial_boundaries(gdf)
        except Exception as e:
            print(f"Error loading country boundaries: {str(e)}")

# Attach the function to the combobox
country_selector.observe(on_country_change, names='value')

# Administrative level boundaries
adm_level_selector = widgets.Dropdown(
    options=[('1', 1), ('2', 2)],
    value=None,
    placeholder='Select ADM level',
    layout=widgets.Layout(width='250px')
)
adm_level_selector_id = f'adm-level-selector-{id(adm_level_selector)}'
adm_level_selector.add_class(adm_level_selector_id)

def on_adm_level_change(change):
    selected_country = country_selector.value

    iso_a3 = country_dict[selected_country]
    adm_level = change['new']
    try:
        gdf = get_adm_data(iso_a3, adm_level)
        plot_geospatial_boundaries(gdf)
    except Exception as e:
        print(f"Error loading ADM{adm_level} boundaries: {str(e)}")


def plot_geospatial_boundaries(gdf, crs: str = "EPSG:4326"):
    gdf = gdf.set_crs(crs)  # Assign WGS 84 CRS by default
    m = folium.Map()
    folium.GeoJson(
        gdf,
        style_function=lambda x: {
            'fillColor': 'none',
            'color': 'black',
            'weight': 1,
            'fillOpacity': 0
        }
    ).add_to(m)
    m.fit_bounds(m.get_bounds())
    map_widget.value = m._repr_html_()
    

# Custom Adm data
# Add these to your existing UI elements
custom_boundaries_radio = widgets.RadioButtons(
    options=['Default boundaries', 'Custom boundaries'],
    disabled=False
)
custom_boundaries_radio_id = f'custom-boundaries-radio-{id(custom_boundaries_radio)}'
custom_boundaries_radio.add_class(custom_boundaries_radio_id)

custom_boundaries_file = widgets.Text(
    value='',
    placeholder='Enter path to custom boundaries file',
    disabled=True, layout=widgets.Layout(width='250px')
)
custom_boundaries_file_id = f'custom-boundaries-file-{id(custom_boundaries_file)}'
custom_boundaries_file.add_class(custom_boundaries_file_id)

custom_boundaries_id_field = widgets.Text(
    value='',
    placeholder='Enter field name for zonal ID',
    disabled=True, layout=widgets.Layout(width='250px')
)
custom_boundaries_id_field_id = f'custom-boundaries-id-field-{id(custom_boundaries_id_field)}'
custom_boundaries_id_field.add_class(custom_boundaries_id_field_id)

custom_boundaries_name_field = widgets.Text(
    value='',
    placeholder='Enter field name for zonal name',
    disabled=True, layout=widgets.Layout(width='250px')
)
custom_boundaries_name_field_id = f'custom-boundaries-name-field-{id(custom_boundaries_name_field)}'
custom_boundaries_name_field.add_class(custom_boundaries_name_field_id)

select_file_button = widgets.Button(
    description='Select File',
    disabled=True,
    button_style='info', layout=widgets.Layout(width='250px')
)

# Custom ADM Functions
def select_file(b):
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    root.attributes('-topmost', True)  # Make the dialog appear on top
    root.geometry(f'+{root.winfo_screenwidth()//2-300}+0')  # Position at the top center of the screen
    file_path = filedialog.askopenfilename(
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
            plot_geospatial_boundaries(gdf)
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

# Hazard

hazard_selector = widgets.Dropdown(options=[
    ('Fluvial Undefended', 'FLUVIAL_UNDEFENDED'), 
    ('Fluvial Defended', 'FLUVIAL_DEFENDED'),
    ('Pluvial Defended', 'PLUVIAL_DEFENDED'), 
    ('Coastal Undefended', 'COASTAL_UNDEFENDED'), 
    ('Coastal Defended', 'COASTAL_DEFENDED')
], value='FLUVIAL_UNDEFENDED', layout=widgets.Layout(width='250px'), style={'description_width': '150px'})
hazard_selector_id = f'hazard-selector-{id(hazard_selector)}'
hazard_selector.add_class(hazard_selector_id)

## Hazard threshold
hazard_threshold_slider = widgets.IntSlider(value=20, min=0, max=200, layout=widgets.Layout(width='250px'))
hazard_threshold_slider_id = f'hazard-threshold-slider-{id(hazard_threshold_slider)}'
hazard_threshold_slider.add_class(hazard_threshold_slider_id)

## Period
period_selector = widgets.Dropdown(options=['2020', '2030', '2050', '2080'], value='2020', layout=widgets.Layout(width='250px'))
period_selector_id = f'period-selector-{id(period_selector)}'
period_selector.add_class(period_selector_id)

## Scenario
scenario_selector = widgets.Dropdown(options=['SSP1-2.6', 'SSP2-4.5', 'SSP3-7.0', 'SSP5-8.5'], value='SSP3-7.0', layout=widgets.Layout(width='250px'))
scenario_selector_id = f'scenario-selector-{id(scenario_selector)}'
scenario_selector.add_class(scenario_selector_id)

## Hazard return periods
return_periods_selector = widgets.SelectMultiple(
    options=[5, 10, 20, 50, 100, 200, 500, 1000],
    value=[5, 10, 20, 50, 100, 200, 500, 1000],
    rows=8,
    disabled=False,
    layout=widgets.Layout(width='250px'))
return_periods_selector_id = f'return_periods-selector-{id(return_periods_selector)}'
return_periods_selector.add_class(return_periods_selector_id)

# Function to update scenario dropdown visibility
def update_scenario_visibility(*args):
    scenario_selector.layout.display = 'none' if period_selector.value == '2020' else 'block'

period_selector.observe(update_scenario_visibility, 'value')
update_scenario_visibility()

# Exposure
exposure_selector = widgets.SelectMultiple(options=[
    ('Population', 'POP'),
    ('Built-up', 'BU'),
    ('Agriculture', 'AGR')
], value=['POP'], layout=widgets.Layout(width='250px'))
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

# Vulnerability

# Create a new output widget for the preview chart and class edges table
approach_box = widgets.Output(layout=widgets.Layout(width='280px', height='250px'))

approach_selector = widgets.Dropdown(options=[('Classes', 'Classes'), ('Function', 'Function')], value='Function', layout=widgets.Layout(width='250px'))
approach_selector_id = f'approach-selector-{id(approach_selector)}'
approach_selector.add_class(approach_selector_id)

# For approach = function, preview impact function
def preview_impact_func(*args):
    if approach_selector.value != 'Function':
        return
    
    with approach_box:
        clear_output(wait=True)
        selected_exposures = exposure_selector.value
        selected_country = country_selector.value
        
        if not selected_country:
            print("Please select a country first.")
            return
        
        # Get the ISO_A3 code for the selected country
        iso_a3 = country_dict.get(selected_country, False)
        if not iso_a3:
            print(f"Error: Could not find ISO_A3 code for {selected_country}")
            return
        
        # Get the World Bank region from the countries.csv file
        wb_region = df.loc[df['ISO_A3'] == iso_a3, 'WB_REGION'].values[0]
        
        if selected_exposures:
            steps = np.arange(0, 6, 0.1)
            fig, ax = plt.subplots(figsize=(4, 3))
            
            for exposure in selected_exposures:
                if exposure == 'POP':
                    damage_factor = lambda x: FL_mortality_factor(x*100)
                elif exposure == 'BU':
                    damage_factor = lambda x: FL_damage_factor_builtup(x*100, wb_region)
                elif exposure == 'AGR':
                    damage_factor = lambda x: FL_damage_factor_agri(x*100, wb_region)
                else:
                    print(f"Unknown exposure category: {exposure}")
                    continue
                
                _, = ax.plot([damage_factor(x) for x in steps], label=exposure)
            
            ax.grid(True)
            ax.legend()
            
            label_steps = range(0, len(steps)+10, 10)
            ax.set_xticks(label_steps)
            ax.set_xticklabels([i / 10 for i in label_steps])
            ax.set_xlabel("Water depth (m)")
            ax.set_ylabel("Impact Factor")
            
            plt.title(f"Impact Functions for {selected_country}")
            plt.tight_layout()
            display(fig)
            plt.close(fig)
        else:
            print("Please select at least one exposure category")
                
# Function to update the preview when relevant widgets change
def update_preview(*args):
    preview_impact_func()

class_edges_table = widgets.VBox()

## Define add_class_button before using it
add_class_button = widgets.Button(description="Add Class", layout=widgets.Layout(width='150px'))

# For approach = classes, define class edges
class_edges_table = widgets.VBox()

# Functions to dynamically add class edges
def create_class_row(index):
    delete_button = widgets.Button(description="Delete", layout=widgets.Layout(width='70px'))
    row = widgets.HBox([
        widgets.Label(f'Class {index}:', layout=widgets.Layout(width='100px')),
        widgets.FloatText(value=0.0, description='', layout=widgets.Layout(width='100px')),
        delete_button
    ])
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

def update_class_edges_table(*args):
    approach_box.clear_output()
    with approach_box:
        if approach_selector.value == 'Classes':
            # Clear existing table
            class_edges_table.children = []
            # Add initial class rows
            class_edges_table.children = [create_class_row(i) for i in range(1, 4)]
            # Add the "Add Class" button
            class_edges_table.children += (add_class_button,)
            update_delete_buttons()
            display(class_edges_table)
        else:
            preview_impact_func()

    # Ensure at least one class remains
    if len(class_edges_table.children) == 1:  # Only "Add Class" button remains
        class_edges_table.children = [create_class_row(1)] + list(class_edges_table.children)
        update_delete_buttons()

approach_selector.observe(update_class_edges_table, 'value')

preview_chk = notebook_utils.preview_chk

# Observe changes in relevant widgets
country_selector.observe(update_preview, names='value')
adm_level_selector.observe(update_preview, names='value')
custom_boundaries_radio.observe(update_preview, names='value')
custom_boundaries_file.observe(update_preview, names='value')
exposure_selector.observe(update_preview, names='value')
approach_selector.observe(update_preview, names='value')

# Create components for the four sections
country_boundaries = widgets.VBox([
    widgets.Label("Country:"),
    country_selector,
    widgets.Label("Administrative Level:"),
    adm_level_selector,
    widgets.Label("Boundaries:"),
    custom_boundaries_radio,
    select_file_button,
    custom_boundaries_file,
    custom_boundaries_id_field,
    custom_boundaries_name_field
])

hazard_info = widgets.VBox([
    widgets.Label("Hazard process:"),
    hazard_selector,
    widgets.Label("Min threshold:"),
    hazard_threshold_slider,
    widgets.Label("Reference period:"),
    period_selector,
    widgets.Label("Climate scenario:"),
    scenario_selector,
    widgets.Label("Return periods:"),
    return_periods_selector
])

exposure_category = widgets.VBox([
    widgets.Label("Exposure Category:"),
    exposure_selector,
    widgets.Label("Exposure Data:"),
    custom_exposure_radio,
    custom_exposure_container
])

vulnerability_approach = widgets.VBox([
    widgets.Label("Vulnerability Approach:"),
    approach_selector,
    approach_box
])

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
info_box = widgets.Textarea(
    value='Hover over items for descriptions.',
    disabled=True,
    layout=widgets.Layout(width='350px', height='100px')
)
info_box.add_class('info-box')

# Button to run the script
run_button = notebook_utils.run_button

# Functions to run the analysis
def validate_input():
    output.clear_output()
    
    # Check ISO_A3 code
    print("Checking country boundaries...")
    selected_country = country_selector.value
    iso_a3 = country_dict.get(selected_country)
    if not iso_a3:
        print(f"Error: {selected_country} is not a valid country selection.")
        return False

    params = {
        'where': f"ISO_A3 = '{iso_a3}'",
        'outFields': 'ISO_A3',
        'returnDistinctValues': 'true',
        'f': 'json'
    }
    
    url = f"{common.rest_api_url}/5/query"
    response = requests.get(url=url, params=params)

    if response.status_code != 200:
        print("Error: Unable to validate country code. Please ensure you are connected to the internet.")
        return False

    data = response.json()
    if not 'features' in data.keys():
        print(f"Error: {iso_a3} is not a valid ISO_A3 code.")
        return False
    
    # Preview only possible if several return periods are selected
    if len(return_periods_selector.value) == 1 and preview_chk.value:
        print("Cannot preview results if only one return period is selected.")
        return False
    
    # Check use of custom boundaries    
    if custom_boundaries_radio.value == 'Custom boundaries':
        if not all([custom_boundaries_id_field.value, custom_boundaries_name_field.value]):
            print("Error: Custom boundaries ID and Name fields must be specified.")
            return False          
        if not custom_boundaries_file.value: 
            print("Error: Custom boundaries file not specified.")
            return False

    # Check class thresholds
    print("Checking class thresholds...")
    if approach_selector.value == 'Classes':
        class_values = [child.children[1].value for child in class_edges_table.children[:-1]]  # Exclude "Add Class" button
        if len(class_values) > 1:
            is_seq = np.all(np.diff(class_values) > 0)
            if not is_seq:
                print(f"Error: Class thresholds must be in increasing  order.")
                return False
            
    if custom_boundaries_radio.value == 'Default boundaries' and adm_level_selector.value is None:
        print("Error: Please select an Administrative Level when working with default boundaries.")
        return False
                
    print("User input accepted!")
    return True

def run_analysis_script(b):
    with output:
        output.clear_output(wait=True)
        
        if not validate_input():
            return 

        # Gather input values
        country = country_dict.get(country_selector.value, False)
        if not country:
            print("Error: Invalid country selection.")
            return
        
        # Rest of the input gathering remains the same
        haz_cat = hazard_selector.value
        period = period_selector.value
        scenario = scenario_selector.value if period != '2020' else ''
        return_periods = list(return_periods_selector.value)
        exp_cat_list = list(exposure_selector.value)
        exp_year = '2020'  # This is fixed as per the original script
        adm_level = adm_level_selector.value
        analysis_type = approach_selector.value
        min_haz_slider = hazard_threshold_slider.value
        
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
        df = pd.read_csv('countries.csv')
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
    
        start_time = time.perf_counter()

        print(f"Starting analysis for {iso_to_country[country]} ({country})...")
        
        # Validate exp_nam_list
        if len(exp_nam_list) != len(exp_cat_list):
            print("ERROR: Parameter 'exp_nam_list' should have the same length as 'exp_cat_list'")
            return
        
        # Initialize the folium preview map before the loop
        m = folium.Map(location=[0, 0], zoom_start=5, draw_control=False, scale_control=False, measure_control=False)

        # Initialize variables
        minx, miny, maxx, maxy = float('inf'), float('inf'), float('-inf'), float('-inf')
        summary_dfs, charts, layers, colormaps = [], [], [], []
        
        # Prepare Excel writer
        excel_file, gpkg_file = prepare_excel_gpkg_files(country, adm_level, haz_cat, period, scenario)

        # Use ExcelWriter as a context manager
        # Run analysis for each exposure category
        for i in range(len(exp_cat_list)):
            exp_cat = exp_cat_list[i]
            exp_nam = exp_nam_list[i]
            print(f"Running analysis for {exp_cat}...")
            result_df = run_analysis(country, haz_type, haz_cat, period, scenario, return_periods, min_haz_slider,
                            exp_cat, exp_nam, exp_year, adm_level, analysis_type, class_edges, 
                            save_check_raster, n_cores, use_custom_boundaries=use_custom_boundaries,
                            custom_boundaries_file_path=custom_boundaries_file_path, custom_code_field=custom_code_field,
                            custom_name_field=custom_name_field, wb_region=wb_region)
            
            if result_df is None:
                print("Encountered Exception! Please fix issue above.")
                return
            
            sheet_name = prepare_sheet_name(analysis_type, return_periods, exp_cat)
                        
            saving_excel_and_gpgk_file(result_df, excel_file, sheet_name, gpkg_file, exp_cat)

            # Create summary DataFrame
            summary_df = create_summary_df(result_df, return_periods, exp_cat)
            summary_dfs.append(summary_df)

            if preview_chk.value:
                # Add each result as a layer
                layer, colormap = plot_results(result_df, exp_cat, analysis_type)
                if layer is not None:
                    layers.append(layer)
                    colormaps.append(colormap)
                    # Update the overall bounding box using result_df
                    bounds = result_df.total_bounds
                    minx = min(minx, bounds[0])
                    miny = min(miny, bounds[1])
                    maxx = max(maxx, bounds[2])
                    maxy = max(maxy, bounds[3])
                        
        # Combine all summary DataFrames
        if summary_dfs:
            combined_summary = prepare_and_save_summary_df(summary_dfs, exp_cat_list, excel_file, return_file=True)
 
            # Add custom exposure information
            excel_writer = pd.ExcelWriter(excel_file, engine='openpyxl', mode='a', if_sheet_exists='replace')
            row_offset = len(combined_summary) + 4  # Start two rows below the table
            for i, exp_cat in enumerate(exp_cat_list):
                if custom_exposure_radio.value == 'Custom exposure':
                    custom_name = custom_exposure_container.children[i].value
                    if custom_name:
                        excel_writer.sheets['Summary'].cell(row=row_offset, column=1, value=f"Custom exposure layer for {exp_cat}: {custom_name}")
                        row_offset += 1

        # Generate charts only for Function approach
        if analysis_type == "Function" and preview_chk.value:
            colors = {'POP': 'blue', 'BU': 'orange', 'AGR': 'green'}
            charts = [create_eai_chart(combined_summary, exp_cat, period, scenario, colors[exp_cat]) 
                     for exp_cat in exp_cat_list]
        else:
            charts = []

        print(f"Analysis completed in {time.perf_counter() - start_time:.2f} seconds")
        print(f"Results saved to Excel file: {excel_file}")
        print(f"Results saved to GeoPackage file: {gpkg_file}")

        # Plot results if preview is checked
        if preview_chk.value and minx != float('inf'):
            center_lat = (miny + maxy) / 2
            center_lon = (minx + maxx) / 2
            m.location = [center_lat, center_lon]
            m.fit_bounds([[miny, minx], [maxy, maxx]])
            print("Plotting results preview as map...")

            # Add layers to the map
            for layer in layers:
                layer.add_to(m)

            # Add colormaps to the map
            for colormap in colormaps:
                colormap.add_to(m)

            # Create a custom layer control
            folium.LayerControl(position='topright', collapsed=False).add_to(m)

            # Add the MiniMap
            MiniMap(toggle_display=True, position='bottomright').add_to(m)

            # Add the Fullscreen button
            Fullscreen(position='bottomleft').add_to(m)

            # Update the map_widget with the new map
            map_widget.value = m._repr_html_()
                
            with chart_output:
                clear_output(wait=True)
                # Display charts only once
                for chart in charts:
                    display(chart)
                    plt.close(chart)  # Close the figure after displaying

run_button.on_click(run_analysis_script)

def create_eai_chart(dfData, exp_cat, period, scenario, color):
    # Defining the title and sub-title
    title = f'Flood x {exp_cat} EAI - {period} {scenario}'
    subtitle = 'Exceedance frequency curve'

    # Defining the x- and y-axis data and text
    x = dfData['Freq'].values
    y = dfData[f'{exp_cat}_impact'].values
    xlbl = 'Frequency'
    ylbl = f'Impact ({exp_cat.lower()})'

    # Defining if plotting total EAI
    txtTotal = True
    xpos = 0.70
    totEAI = dfData[f'{exp_cat}_EAI'].sum()

    # Defining the plot style and colours
    sns.set_style('whitegrid')
    plt_color = color
    xFreqAsRP = True

    # Increase font sizes
    plt.rcParams.update({'font.size': 12})
    plt.rcParams.update({'axes.labelsize': 14})
    plt.rcParams.update({'axes.titlesize': 16})

    # Creating the plot with smaller size
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(x, y, color=plt_color, lw=2, marker="o", markersize=6)
    ax.fill_between(x, 0, y, alpha=.3, color=plt_color)
    ax.set(xlim=(0, max(x)), ylim=(0, max(y)*1.05), xticks=np.linspace(0, max(x), 5))
    ax.ticklabel_format(style='plain', axis='y')
    ax.yaxis.set_major_formatter(StrMethodFormatter('{x:,.0f}'))
    ax.set_xlabel(xlbl, fontsize=14)
    ax.set_ylabel(ylbl, fontsize=14)
    ax.set_title(f'{title}\n{subtitle}', fontsize=16, fontweight='bold')

    if xFreqAsRP:
        rp_lbl = dfData['RP'].values.tolist()
        rp_lbl = ['RP '+str(item) for item in rp_lbl]
        for i, rp in enumerate(rp_lbl):
            ax.text(x[i]/max(x)+0.01, y[i]/(max(y)*1.05)+0.01, rp, color='#4D4D4D',
                    ha='left', va='bottom', transform=ax.transAxes, fontsize=10,
                    bbox=dict(facecolor='#FAFAFA', edgecolor='#4D4D4D', boxstyle='round,pad=0.1', alpha=0.4))

    if txtTotal:
        vtext = f'EAI = {totEAI:,.2f}'
        ax.text(xpos, 0.8, vtext, fontsize=15, color='black', fontweight='bold',
                ha='left', va='bottom', transform=ax.transAxes, 
                bbox=dict(facecolor='#FAFAFA', edgecolor='#4D4D4D', boxstyle='square,pad=0.4', alpha=1))

    plt.tight_layout()
    return fig

# Displaying the GUI
# Create the header widget
header = notebook_utils.create_header_widget(hazard="FL")

# Footer
footer = notebook_utils.create_footer()

# Output area
output = notebook_utils.output_widget
chart_output = notebook_utils.chart_output

# Sidebar
sidebar = notebook_utils.create_sidebar(info_box, tabs, output, footer)

# Create an HTML widget to display the map
map_widget = notebook_utils.map_widget

# Chart output area (below the map)
chart_output = notebook_utils.chart_output

# Combine map and chart output, get full ui and final layout
map_and_chart, content_layout, final_layout = notebook_utils.get_ui_components(sidebar, header)

# JavaScript to handle hover events and update the info box
js_code = notebook_utils.create_js_code(
    country_selector_id, adm_level_selector_id, custom_boundaries_radio_id, custom_boundaries_file_id,
    custom_boundaries_id_field_id, custom_boundaries_name_field_id, hazard_selector_id, 
    hazard_threshold_slider_id, period_selector_id, scenario_selector_id, return_periods_selector_id, 
    exposure_selector_id, custom_exposure_radio_id, custom_exposure_textbox_id, approach_selector_id
)

def initialize_tool():
    # Display the layout and inject the JavaScript code
    display(final_layout)
    display(HTML(js_code))

    # Initial updates
    update_custom_boundaries_visibility()
    update_custom_exposure_visibility()
    update_class_edges_table()
    update_preview_availability()

def update_preview_availability(*args):
    """Update preview checkbox availability based on analysis type"""
    preview_chk.disabled = approach_selector.value == 'Classes'
    if approach_selector.value == 'Classes':
        preview_chk.value = False

# Add observer to approach selector
approach_selector.observe(update_preview_availability, 'value')
