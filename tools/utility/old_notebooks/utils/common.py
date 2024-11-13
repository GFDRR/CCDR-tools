import ipywidgets as widgets
from collections import OrderedDict

exp_cat_dd = widgets.Dropdown(
    options=[("Population", "pop"), ("Built-up", "builtup"), ("Agriculture", "agri")],
    value='pop',
    description='Exposure Category:',
    style={'description_width': 'initial'}
)

adm3_dd = widgets.Dropdown(
    options=['ADM1', 'ADM2', 'ADM3'],
    value='ADM2',
    description='Administrative Unit Level:',
    style={'description_width': 'initial'}
)

adm4_dd = widgets.Dropdown(
    options=['ADM1', 'ADM2', 'ADM3', 'ADM4'],
    value='ADM2',
    description='Administrative Unit Level:',
    style={'description_width': 'initial'}
)

save_inter_rst_chk = widgets.Checkbox(
    value=False,
    description='Export Intermediate Rasters',
    tooltip='Save rasters generated between each step (saves to nominated output directory)',
    disabled=False,
    indent=False
)

run_button = widgets.Button(
    description='Run Analysis',
    button_style='', # 'success', 'info', 'warning', 'danger' or ''
    tooltip='Click to run analysis with selected options',
)

reset_display_button = widgets.Button(
    description='Reset',
    button_style='', # 'success', 'info', 'warning', 'danger' or ''
    tooltip='Reset display',
)

rcp_scenario_dd = widgets.Dropdown(
    options=["2.6", "4.5", "8.5"],
    value="4.5",
    description='RCP Scenario:',
    style={'description_width': 'initial'}
)

time_horizon_dd = widgets.Dropdown(
    options=[2040, 2060, 2080, 2100],
    value=2060,
    description='Time Horizon:',
    style={'description_width': 'initial'}
)


def create_class_edges(class_list, min_val, max_val, step_size):
    
    class_edges = OrderedDict({
        f'class_{i+1}': widgets.BoundedFloatText(
            value=k,
            min = min_val,
            max = max_val,
            step = step_size,
            description=f'Class {i+1}:',
        tooltip=f'Minimum value of class {i+1}. Value must be less than the next entry.',
        disabled=False
        ) for i, k in enumerate(class_list)
    })
    
    return class_edges
    
    
def create_country_dd(option_list, default_value):
    
    country_dd = widgets.Dropdown(
        options=option_list,
        value = default_value,
        description='Country:',
        style={'description_widgth': 'initial'}
    )
    
    return country_dd


def create_min_haz_slider(value, min_value, max_value, step_size):
    
    min_haz_slider = widgets.FloatSlider(
        value = value,
        min = min_value, 
        max = max_value, 
        step = step_size,
        description="Minimum Hazard Threshold",
        style={'description_width': 'initial'}
    )
    
    return min_haz_slider