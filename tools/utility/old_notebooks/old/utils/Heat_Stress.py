import ipywidgets as widgets

country_list = {
    'country_options': [('Nepal', 'NPL'), ('Pakistan', 'PAK'),('Bangladesh', 'BGD'),('Ghana', 'GHA'),
            ('Ethiopia', 'ETH'), ('Burkina Faso', 'BFA'), ('Mali', 'MLI'), ('Niger', 'NER'),
            ('Chad', 'TCD'), ('Mauritania', 'MRT'), ('Nigeria', 'NGA'), ('Dominican Republic', 'DOM'), 
            ('Papua New Guinea', 'PNG'), ('Guinea-Bissau', 'GNB')],
    'default_value': 'NPL'
}

analysis_app_dd = widgets.Dropdown(
    options=["Classes"],
    value="Classes",
    description='Analysis Approach:',
    style={'description_width': 'initial'}
)

class_edges_list = {
    'class_list': [18, 23, 28, 30],
    'min_val': 18.0, 
    'max_val': 50.0,
    'step_size':1.0
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
    "MRT": 159,
    "NGA": 182,
    "PNG": 'PG',
    "GNB": 'GW'
}