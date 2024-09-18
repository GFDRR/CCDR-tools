import ipywidgets as widgets

country_list = {
    'country_options': [('Nepal', 'NPL'), ('Pakistan', 'PAK'),('Bangladesh', 'BGD'),('Ghana', 'GHA'),
            ('Ethiopia', 'ETH'), ('Burkina Faso', 'BFA'), ('Mali', 'MLI'), ('Niger', 'NER'),
            ('Chad', 'TCD'), ('Mauritania', 'MRT')],
    'default_value': 'NPL'  
}

analysis_app_dd = widgets.Dropdown(
    options=["Classes"],
    value="Classes",
    description='Analysis Approach:',
    style={'description_width': 'initial'}
)

class_edges_list = {
    'class_list': [7.5, 12.5, 22.5, 32.5, 37.5],
    'min_val': 0.0, 
    'max_val': 100.0,
    'step_size':0.5
}

country_code_map = {
    "NPL": 175,
    "PAK": 188,
    "BGD": 23,
    "GHA": 94,
    "ETH": 79,
    "BFA": 42,
    "MLI": 155,
    "NER": 181,
    "TCD": 50,
    "MRT": 159
}