import pytest
from tools.code.input_utils import get_layer_id_for_adm
from tools.code.common import rest_api_url
import requests


def test_get_layer_id_for_adm():
    
    # Getting actual data
    response = requests.get(f"{rest_api_url}/layers", params={'f': 'json'})
    layers_info = response.json().get('layers', [])
    
    # Case 1: Test ADM Level 1    
    adm_level_1 = get_layer_id_for_adm(adm_level=1)
    assert layers_info[adm_level_1]['name'] == 'WB_GAD_ADM1'
    
    # Case 2: Test ADM Level 2
    adm_level_2 = get_layer_id_for_adm(adm_level=2)
    assert layers_info[adm_level_2]['name'] == 'WB_GAD_ADM2'
    
    # Case 3: Test ADM Level 0
    adm_level_0 = get_layer_id_for_adm(adm_level=0)
    assert layers_info[adm_level_0]['name'] == 'WB_GAD_ADM0'
    
    
    # Case 4: Testing 'incorrect' ADM level
    with pytest.raises(ValueError) as exc_info:
        _ = get_layer_id_for_adm(adm_level='xyz')        
    assert str(exc_info.value) == 'Layer matching WB_GAD_ADMxyz not found.'
    
    with pytest.raises(ValueError) as exc_info:
        _ = get_layer_id_for_adm(adm_level=None)
    assert str(exc_info.value) == 'Layer matching WB_GAD_ADMnone not found.'
    
    
    
    
    