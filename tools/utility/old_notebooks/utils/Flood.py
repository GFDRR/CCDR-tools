import ipywidgets as widgets

country_list = {
    'country_options': [('Nepal', 'NPL'), ('Pakistan', 'PAK'),('Bangladesh', 'BGD'),('Ghana', 'GHA'),
            ('Ethiopia', 'ETH'), ('Burkina Faso', 'BFA'), ('Mali', 'MLI'), ('Niger', 'NER'),
            ('Chad', 'TCD'), ('Mauritania', 'MRT'), ('Nigeria', 'NGA'), ('Dominican Republic', 'DOM'), 
            ('Papua New Guinea', 'PNG'), ('Guinea-Bissau', 'GNB')],
    'default_value': 'NPL'
}

analysis_app_dd = widgets.Dropdown(
    options=["Classes", "Function"],
    value="Function",
    description='Analysis Approach:',
    style={'description_width': 'initial'}
)

class_edges_list = {
    'class_list': [0.01, 0.15, 0.5, 1, 1.5, 2],
    'min_val': 0.01, 
    'max_val': 10.0,
    'step_size':0.01
}

haz_slider_vals = {
    'value': 0.5,
    'min_value': 0.01,
    'max_value': 10.0, 
    'step_size': 0.01,
}

country_code_map = {
    "NPL": 175,
    "PAK": 188,
    "BGD": 23,
    "GHA": 94,
    "ETH": 79,
    "BFA": 'BFA',
    "MLI": 155,
    "NER": 181,
    "TCD": 50,
    "MRT": 159,
    "NGA": 182,
    "DOM": 'DO',
    "PNG": 'PG',
    "GNB": 'GW'
}