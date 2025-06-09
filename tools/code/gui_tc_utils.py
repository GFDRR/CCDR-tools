import common
import folium
from folium.plugins import MiniMap, Fullscreen
import geopandas as gpd
from IPython.display import display, clear_output, HTML
import ipywidgets as widgets
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import time
import tkinter as tk
from tkinter import filedialog

from damageFunctions import TC_damage_factor_builtup
from input_utils import get_adm_data
import notebook_utils
from runAnalysis import (
    run_analysis, plot_results, create_summary_df, prepare_excel_gpkg_files,
    prepare_sheet_name, saving_excel_and_gpgk_file, prepare_and_save_summary_df
)


DATA_DIR = common.DATA_DIR
OUTPUT_DIR = common.OUTPUT_DIR

# Define hazard type
haz_type = 'TC'

# Load country data
df = pd.read_csv('countries.csv')
country_dict = dict(zip(df['NAM_0'], df['ISO_A3']))
iso_to_country = dict(zip(df['ISO_A3'], df['NAM_0']))

# Create the Combobox widget with auto-complete functionality
country_selector = notebook_utils.create_country_selector_widget(list(country_dict.keys()))
country_selector_id = f'country-selector-{id(country_selector)}'
country_selector.add_class(country_selector_id)


def create_initial_map():
    m = folium.Map(location=[0, 0], zoom_start=2)
    
    try:
        rp100_layer = gpd.read_file(f"{DATA_DIR}/HZD/GLB/STORM/RP100_WS.gpkg", layer='RP100_WS')
        
        # Define wind speed classes and colors
        wind_breaks = [10, 20, 30, 40, 50, float('inf')]
        colors = ['#b1f162', '#fff71d', '#ffb300', '#ff0400', '#fe00d4']
        
        def get_color(wind_speed):
            for i, (lower, upper) in enumerate(zip(wind_breaks[:-1], wind_breaks[1:])):
                if lower <= wind_speed < upper:
                    return colors[i]
            return colors[-1]
        
        def style_function(feature):
            wind_speed = feature['properties']['WIND_MIN']
            return {
                'fillColor': get_color(wind_speed),
                'fillOpacity': 0.7,
                'color': 'black',
                'weight': 0
            }
        
        # Add the wind speed layer
        wind_layer = folium.GeoJson(
            rp100_layer,
            name='RP100 Wind Speed',
            style_function=style_function
        )
        wind_layer.add_to(m)
        
        # Add a legend
        legend_html = '''
        <div style="position: fixed; bottom: 20px; left: 20px; z-index: 1000; background-color: white; 
                    padding: 10px; border-radius: 5px; border: 2px solid grey;">
            <p style="margin-bottom: 5px;"><strong>Wind Speed (m/s)</strong></p>
        '''
        for i, (lower, upper) in enumerate(zip(wind_breaks[:-1], wind_breaks[1:])):
            if upper == float('inf'):
                label = f'≥ {lower}'
            else:
                label = f'{lower} - {upper}'
            legend_html += f'''
            <p style="margin: 2px;">
                <span style="background-color: {colors[i]}; display: inline-block; width: 20px; height: 20px;"></span>
                {label}
            </p>'''
        legend_html += '</div>'
        
        m.get_root().html.add_child(folium.Element(legend_html))
        
        # Add layer control
        folium.LayerControl().add_to(m)
        
    except Exception as e:
        print(f"Could not load RP100_WS layer: {str(e)}")
    
    return m


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


def plot_geospatial_boundaries(gdf, crs: str = "EPSG:4326"):
    gdf = gdf.set_crs(crs)  # Assign WGS 84 CRS by default
    m = folium.Map()

    # Add the wind speed layer first
    try:
        rp100_layer = gpd.read_file(f"{DATA_DIR}/HZD/GLB/STORM/RP100_WS.gpkg", layer='RP100_WS')
        
        # Define wind speed classes and colors
        wind_breaks = [10, 20, 30, 40, 50, float('inf')]
        colors = ['#b1f162', '#fff71d', '#ffb300', '#ff0400', '#fe00d4']
        
        def get_color(wind_speed):
            for i, (lower, upper) in enumerate(zip(wind_breaks[:-1], wind_breaks[1:])):
                if lower <= wind_speed < upper:
                    return colors[i]
            return colors[-1]
        
        def style_function(feature):
            wind_speed = feature['properties']['WIND_MIN']
            return {
                'fillColor': get_color(wind_speed),
                'fillOpacity': 0.7,
                'color': 'black',
                'weight': 0
            }
        
        # Add the wind speed layer
        wind_layer = folium.GeoJson(
            rp100_layer,
            name='RP100 Wind Speed',
            style_function=style_function
        )
        wind_layer.add_to(m)
        
        # Add a legend
        legend_html = '''
        <div style="position: fixed; bottom: 20px; left: 20px; z-index: 1000; background-color: white; 
                    padding: 10px; border-radius: 5px; border: 2px solid grey;">
            <p style="margin-bottom: 5px;"><strong>Wind Speed (m/s)</strong></p>
        '''
        for i, (lower, upper) in enumerate(zip(wind_breaks[:-1], wind_breaks[1:])):
            if upper == float('inf'):
                label = f'≥ {lower}'
            else:
                label = f'{lower} - {upper}'
            legend_html += f'''
            <p style="margin: 2px;">
                <span style="background-color: {colors[i]}; display: inline-block; width: 20px; height: 20px;"></span>
                {label}
            </p>'''
        legend_html += '</div>'
        
        m.get_root().html.add_child(folium.Element(legend_html))
        
    except Exception as e:
        print(f"Could not load RP100_WS layer: {str(e)}")

    # Add the boundary layer
    folium.GeoJson(
        gdf,
        name='Administrative Boundaries',
        style_function=lambda x: {
            'fillColor': 'none',
            'color': 'black',
            'weight': 1,
            'fillOpacity': 0
        }
    ).add_to(m)

    # Add layer control
    folium.LayerControl().add_to(m)
    
    # Get the total bounds of all features
    total_bounds = gdf.total_bounds  # Returns [minx, miny, maxx, maxy]
    m.fit_bounds([[total_bounds[1], total_bounds[0]], [total_bounds[3], total_bounds[2]]])
  
    map_widget.value = m._repr_html_()

# Custom Adm data
# Add these to your existing UI elements
custom_boundaries_radio = notebook_utils.custom_boundaries_radio
custom_boundaries_radio_id = f'custom-boundaries-radio-{id(custom_boundaries_radio)}'
custom_boundaries_radio.add_class(custom_boundaries_radio_id)

custom_boundaries_file = notebook_utils.custom_boundaries_file
custom_boundaries_file_id = f'custom-boundaries-file-{id(custom_boundaries_file)}'
custom_boundaries_file.add_class(custom_boundaries_file_id)

custom_boundaries_id_field = notebook_utils.custom_boundaries_id_field
custom_boundaries_id_field_id = f'custom-boundaries-id-field-{id(custom_boundaries_id_field)}'
custom_boundaries_id_field.add_class(custom_boundaries_id_field_id)

custom_boundaries_name_field = notebook_utils.custom_boundaries_name_field
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
    ('Strong Wind', 'SW')     
], value='SW', layout=widgets.Layout(width='250px'), style={'description_width': '150px'})
hazard_selector_id = f'hazard-selector-{id(hazard_selector)}'
hazard_selector.add_class(hazard_selector_id)

## Hazard threshold
hazard_threshold_slider = widgets.IntSlider(value=20, min=10, max=500, layout=widgets.Layout(width='250px'))
hazard_threshold_slider_id = f'hazard-threshold-slider-{id(hazard_threshold_slider)}'
hazard_threshold_slider.add_class(hazard_threshold_slider_id)

## Period
period_selector = widgets.Dropdown(options=['2020','2050'], value='2020', layout=widgets.Layout(width='250px'))
period_selector_id = f'period-selector-{id(period_selector)}'
period_selector.add_class(period_selector_id)

## Scenario
scenario_selector = widgets.Dropdown(options=['SSP5-8.5'], value='SSP5-8.5', layout=widgets.Layout(width='250px'))
scenario_selector_id = f'scenario-selector-{id(scenario_selector)}'
scenario_selector.add_class(scenario_selector_id)

## Hazard return periods
return_periods_selector = widgets.SelectMultiple(
    options=[10, 20, 50, 100, 200, 500, 1000],
    value=[10, 20, 50, 100, 200, 500, 1000],
    rows=7,
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

# Vulnerability

# Create a new output widget for the preview chart and class edges table
approach_box = widgets.Output(layout=widgets.Layout(width='280px', height='250px'))

approach_selector = notebook_utils.approach_selector
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
        
        if selected_exposures:
            # Use appropriate wind speed range for TC damage functions (0-300 m/s)
            steps = np.arange(0, 300, 1)
            fig, ax = plt.subplots(figsize=(4, 3))
            
            for exposure in selected_exposures:
                if exposure in ['BU']:
                    damage_factor = lambda x: TC_damage_factor_builtup(x, iso_a3)
                else:
                    print(f"Tropical cyclone damage functions not available for {exposure}")
                    continue
                
                _, = ax.plot(steps, [damage_factor(x) for x in steps], label=exposure)
            
            ax.grid(True)
            ax.legend()
            
            ax.set_xlabel("Wind speed (m/s)")
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

## Define add_class_button before using it
add_class_button = widgets.Button(description="Add Class", layout=widgets.Layout(width='150px'))

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
country_boundaries = notebook_utils.create_country_boundaries(
    country_selector, adm_level_selector, custom_boundaries_radio,
    select_file_button, custom_boundaries_file,
    custom_boundaries_id_field, custom_boundaries_name_field
)

hazard_info = notebook_utils.create_hazard_info(
    hazard_selector,
    "Min threshold (m/s):",
    hazard_threshold_slider,
    period_selector,
    scenario_selector,
    return_periods_selector
)

exposure_category = notebook_utils.create_exposure_category(
    custom_exposure_radio, custom_exposure_container
)

vulnerability_approach = notebook_utils.create_vulnerability_approach(
    approach_selector, approach_box    
)

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
    
    return notebook_utils.run_input_checks(
        country_selector, country_dict, haz_type,
        return_periods_selector, preview_chk,
        custom_boundaries_radio, 
        custom_boundaries_id_field,
        custom_boundaries_name_field,
        custom_boundaries_file, 
        approach_selector, class_edges_table
    )


def run_analysis_script(b):
    run_button.distabled = True
    run_button.description = "Analysis Running..."
    try:
        with output:
            output.clear_output(wait=True)
            
            if not validate_input():
                return 

            # Gather input values
            country = country_dict.get(country_selector.value, False)
            if not country:
                print("Error: Invalid country selection.")
                return
                        
            # Input gathering
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
                notebook_utils.write_combined_summary_to_excel(
                    excel_file, combined_summary, exp_cat_list,
                    custom_exposure_radio, custom_exposure_container
                )
                
            # Generate charts only for Function approach
            if analysis_type == "Function" and preview_chk.value:
                colors = {'POP': 'blue', 'BU': 'orange', 'AGR': 'green'}
                title_prefix = "Wind "
                charts = [notebook_utils.create_eai_chart(title_prefix, combined_summary, exp_cat, period, scenario, colors[exp_cat]) 
                        for exp_cat in exp_cat_list]
                
                # Export charts if requested
                if notebook_utils.export_charts_chk.value and charts:
                    notebook_utils.export_charts(
                        common.OUTPUT_DIR, country, haz_cat, period, scenario, charts, exp_cat_list
                    )

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

    except Exception as e:
        print(f"An error occurred during analysis: {str(e)}")
    finally:
        # Re-enable the run button and restore its original text
        run_button.disabled = False 
        run_button.description = "Run Analysis"


run_button.on_click(run_analysis_script)


# Displaying the GUI
# Create the header widget
header = notebook_utils.create_header_widget(hazard="TC")

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
map_and_chart, content_layout, final_layout = notebook_utils.get_ui_components(sidebar, header, map_widget)

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

    # Initialize map with wind speed layer
    m = create_initial_map()
    map_widget.value = m._repr_html_()
    
    # Initial updates
    update_custom_boundaries_visibility()
    update_custom_exposure_visibility()
    update_class_edges_table()
    update_preview_availability()

def update_preview_availability(*args):
    """Update preview checkbox availability based on analysis type"""
    is_classes = approach_selector.value == 'Classes'
    preview_chk.disabled = is_classes
    notebook_utils.export_charts_chk.disabled = is_classes
    if is_classes:
        preview_chk.value = False
        notebook_utils.export_charts_chk.value = False

# Add observer to approach selector
approach_selector.observe(update_preview_availability, 'value')
