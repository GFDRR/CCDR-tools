from base64 import b64encode
from ipywidgets import Checkbox, Button, Layout, HTML, VBox, HBox, Output
from folium import Map


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
        document.querySelector('.info-box textarea').value = 'Select the type of flood hazard.\\nThe DEFENDED option accounts for protection standards set proportional to country GDP; it does not account for geolocated physical defence measures.';
    }};
    document.querySelector('.{hazard_threshold_slider_id}').onmouseover = function() {{
        document.querySelector('.info-box textarea').value = 'Set the minimum hazard threshold, in the unit of the dataset.\\nValues below this threshold will be ignored.';
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


def create_header_widget(img_path:str=None):
    
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
            <h4 style='color: #118AB2; margin: 0; font-size: 1vw; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;'><b>FLOOD HAZARD (FATHOM 3)</b></h4>
        </div>
        <img src="data:image/png;base64,{img_base64}" style="width: 200px; max-width: 200px; height: auto; margin-left: 20px;">
    </div>
    """
    
    return HTML(value=header_html, layout=Layout(width='99%'))
    
preview_chk = Checkbox(
    value=True,
    description='Preview Results',
    disabled=False,
    indent=False
)

# checkbox for exporting charts
export_charts_chk = Checkbox(
    value=False,
    description='Export Charts as PNG',
    disabled=False,
    indent=False
)

run_button = Button(
    description="Run Analysis",
    layout=Layout(width='250px'),
    button_style='danger'
)

def create_footer():
    preview_container = HBox([
        preview_chk,
        export_charts_chk
    ], layout=Layout(width='100%', justify_content='space-around'))
    
    return VBox([
        preview_container,
        HBox([run_button], layout=Layout(display='flex', justify_content='center', width='100%'))
    ], layout=Layout(width='100%', height='100px', padding='10px'))
    
output_widget = Output()
chart_output = Output(layout=Layout(width='100%', height='auto'))

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
    
chart_output = Output(layout={'width': '98%', 'height': 'auto'})
  
map_widget = HTML(
    value=Map(location=[0,0], zoom_start=2)._repr_html_(),
    layout=Layout(width='98%', height='600px')    
)

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