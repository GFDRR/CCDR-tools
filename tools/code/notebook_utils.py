from base64 import b64encode
from ipywidgets import (
    Button,
    Checkbox,
    Dropdown,
    FloatText,
    HBox,
    HTML,
    Layout,
    Label,
    Output,
    RadioButtons,
    SelectMultiple,
    Text,
    Textarea,
    VBox
)
from folium import Map
import common
import numpy as np
import requests


def create_js_code(
    country_selector_id, adm_level_selector_id, custom_boundaries_radio_id,
    custom_boundaries_file_id, custom_boundaries_id_field_id, custom_boundaries_name_field_id,
    hazard_selector_id, hazard_threshold_slider_id, period_selector_id, scenario_selector_id,
    return_periods_selector_id, exposure_selector_id, custom_exposure_radio_id, 
    custom_exposure_textbox_id, approach_selector_id
    ) -> str:
    js_code = js_code = f"""
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
    document.querySelector('.{hazard_selector_id}').onmouseover = function() {{
        document.querySelector('.info-box textarea').value = 'Select the type of hazard process.';
    }};
    document.querySelector('.{hazard_threshold_slider_id}').onmouseover = function() {{
        document.querySelector('.info-box textarea').value = 'Set the minimum hazard threshold, in the unit of the hazard dataset.\\nValues below this threshold will be ignored.';
    }};
    document.querySelector('.{period_selector_id}').onmouseover = function() {{
        document.querySelector('.info-box textarea').value = 'Select the reference time period for the hazard analysis:\\n\\n- Historical baseline: 2020\\n- Future periods: 2030, 2050, 2080';
    }};
    document.querySelector('.{scenario_selector_id}').onmouseover = function() {{
        document.querySelector('.info-box textarea').value = 'Choose the climate scenario for future projections.';
    }};
    document.querySelector('.{return_periods_selector_id}').onmouseover = function() {{
        document.querySelector('.info-box textarea').value = 'Choose the return periods to consider.\\nCtrl + click or drag mouse for multiple choices.\\n\\nReturn period defines the intensity of the hazard in relation to its occurrence probability.\\nWhen using the function approach, the whole range selection is preferred for best results.';
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
        document.querySelector('.info-box textarea').value = 'Select the approach for risk classification: Classes or Function.\\n\\n- Function approach is based on default impact functions for each exposure category.\\n- Classes approach measures the average annual exposure to user-defined hazard thresholds. Thresholds must be inserted in incremental order.';
    }};
    document.querySelector('.{adm_level_selector_id}').onmouseover = function() {{
        document.querySelector('.info-box textarea').value = 'Select the administrative level to aggregate and present the results of the analysis.';
    }};
    </script>"""
    return js_code


def create_header_widget(hazard:str="FL", img_path:str=None):
    
    if hazard == 'FL':
        hazard_text = "FLOOD HAZARD (FATHOM 3)"
    elif hazard == 'TC':
        hazard_text = "TROPICAL CYCLONE HAZARD (STORM v4)"
    
    img_path = 'rdl_logo.png' if img_path is None else img_path
       
    with open(img_path, "rb") as img_file:
        img_base64 = b64encode(img_file.read()).decode('utf-8')
    
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
            <h4 style='color: #118AB2; margin: 0; font-size: 1vw; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;'><b>{hazard_text}</b></h4>
        </div>
        <img src="data:image/png;base64,{img_base64}" style="width: 200px; max-width: 200px; height: auto; margin-left: 20px;">
    </div>
    """
    
    return HTML(value=header_html, layout=Layout(width='99%'))


def create_footer():
    return VBox(
        [
            preview_chk, HBox([run_button], 
            layout=Layout(display='flex', justify_content='center', width='100%'))
        ], layout=Layout(width='100%', height='100px', padding='10px')
    )
    

def create_sidebar(info_box, tabs, output, footer):
    
    sidebar_content = VBox([
        info_box,
        tabs,
        output
    ], layout=Layout(overflow='auto'))

    return VBox([
        sidebar_content,
        footer
    ], layout=Layout(width='370px', height='100%'))


def get_ui_components(sidebar, header):
    
    map_and_chart = VBox(
        [map_widget, chart_output],
        layout=Layout(width='750px', height='100%')
    )
        
    content_layout = HBox(
        [sidebar, map_and_chart],
        layout=Layout(width='100%', height='800px')
    )
    
    final_layout = VBox(
        [header, content_layout],
        layout=Layout(width='100%')
    )

    return map_and_chart, content_layout, final_layout


def create_country_selector_widget(country_options: list[str]):
    
    country_selector = Dropdown(
        options=country_options,
        value=None,
        placeholder='Select Country',
        layout=Layout(width='250px')
    )
    
    return country_selector


def run_input_checks(
    country_selector, country_dict, haz_type,
    return_periods_selector, preview_chk,
    custom_boundaries_radio, 
    custom_boundaries_id_field,
    custom_boundaries_name_field,
    custom_boundaries_file,
    approach_selector,
    class_edges_table
):
    
    # 1 Check ISO_A3 code
    print("Checking country boundaries...")
    selected_country = country_selector.value
    iso_a3 = country_dict.get(selected_country)
    if not iso_a3:
        print(f"Error: {selected_country} is not a valid country selection.")
        return False

    if haz_type == "TC":
        if iso_a3 not in common.tc_region_mapping.keys():
            print(f"Error: {selected_country} is located outside the hazard extent for Tropical Cyclones.")
            return False

    # 2 Validate country code 
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


def create_row_box(index, delete_button):
    return HBox(
        [
            Label(f'Class {index}:', layout=Layout(width='100px')),
            FloatText(value=0.0, description='', layout=Layout(width='100px')),
            delete_button
        ]
    )
    

def create_country_boundaries(
    country_selector, adm_level_selector, custom_boundaries_radio,
    select_file_button, custom_boundaries_file,
    custom_boundaries_id_field, custom_boundaries_name_field
):
    return VBox([
        Label("Country:"),
        country_selector,
        Label("Administrative Level:"),
        adm_level_selector,
        Label("Boundaries:"),
        custom_boundaries_radio,
        select_file_button,
        custom_boundaries_file,
        custom_boundaries_id_field,
        custom_boundaries_name_field
    ])


def create_hazard_info(
    hazard_selector, min_threshold_text, hazard_threshold_slider,
    period_selector, scenario_selector, return_periods_selector
):
    return VBox([
        Label("Hazard process:"),
        hazard_selector,
        Label(min_threshold_text),
        hazard_threshold_slider,
        Label("Reference period:"),
        period_selector,
        Label("Climate scenario:"),
        scenario_selector,
        Label("Return periods:"),
        return_periods_selector,
    ])
    

def create_exposure_category(custom_exposure_radio, custom_exposure_container):
    return VBox([
        Label("Exposure Category:"),
        exposure_selector,
        Label("Exposure Data:"),
        custom_exposure_radio,
        custom_exposure_container
    ])


def create_vulnerability_approach(approach_selector, approach_box):
    return VBox([
        Label("Vulnerability Approach:"),
        approach_selector,
        approach_box
    ])


preview_chk = Checkbox(
    value=True,
    description='Preview Results',
    disabled=False,
    indent=False
)

run_button = Button(
    description="Run Analysis",
    layout=Layout(width='250px'),
    button_style='danger'
)
 
output_widget = Output()
chart_output = Output(layout={'width': '98%', 'height': 'auto'})
  
map_widget = HTML(
    value=Map(location=[0,0], zoom_start=2)._repr_html_(),
    layout=Layout(width='98%', height='600px')    
)

adm_level_selector = Dropdown(
    options=[('1', 1), ('2', 2)],
    value=None,
    placeholder='Select ADM level',
    layout=Layout(width='250px')
)

custom_boundaries_radio = RadioButtons(
    options=['Default boundaries', 'Custom boundaries'],
    disabled=False
)

exposure_selector = SelectMultiple(options=[
    ('Population', 'POP'),
    ('Built-up', 'BU'),
    ('Agriculture', 'AGR')
], value=['POP'], layout=Layout(width='250px'))

custom_boundaries_file = Text(
    value='',
    placeholder='Enter path to custom boundaries file',
    disabled=True, layout=Layout(width='250px')
)

custom_boundaries_id_field = Text(
    value='',
    placeholder='Enter field name for zonal ID',
    disabled=True, layout=Layout(width='250px')
)

custom_boundaries_name_field = Text(
    value='',
    placeholder='Enter field name for zonal name',
    disabled=True, layout=Layout(width='250px')
)

select_file_button = Button(
    description='Select File',
    disabled=True,
    button_style='info', layout=Layout(width='250px')
)

approach_selector = Dropdown(
    options=[
        ('Classes', 'Classes'),
        ('Function', 'Function')
    ],
    value='Function',
    layout=Layout(width='250px')
)

delete_button = Button(
    description="Delete",
    layout=Layout(width='70px')
)

info_box = Textarea(
    value='Hover over items for descriptions.',
    disabled=True,
    layout=Layout(width='350px', height='100px')
)
