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
    'class_list': [0.0001, 0.001, 0.01],
    'min_val': 0.0, 
    'max_val': 10.0,
    'step_size':0.0001
}
