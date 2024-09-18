from tools.code.damageFunctions import mortality_factor, damage_factor_builtup, damage_factor_agri
import numpy as np
import pytest


def test_mortality_factor():
    
    # Case 1: Typical input values
    x = np.array([0, 10, 50, 100, 200])
    expected = np.array([0.00176976, 0.0020376 , 0.00357871, 0.00722308, 0.02898486])    
    result = mortality_factor(x)
    assert np.allclose(result, expected, rtol=1e-8)
    
    # TODO
    # Case 2: Test edge cases
    
    # TODO
    # Case 3: Test that clipping to 0 and 1 works out 
    
    
    # Case 4: Failing with Invalid input types
    with pytest.raises(TypeError):
        mortality_factor("invalid INPUT!")
    
    # Case 5: Failing with None passed
    with pytest.raises(TypeError):
        mortality_factor()
        
    with pytest.raises(TypeError):
        mortality_factor(None)


def test_damage_factor_builtup():
    
    # We will reuse this np array through the tests
    x = np.array([0, 1, 5, 10, 15, 25, 50, 100, 1000])
    test_outcomes = lambda x, y: np.allclose(x, y, rtol=1e-5)

    
    ## Case 1: Test with sample values for African region
    expected_africa = np.array([
        0.00440468, 0.00622345, 0.0177687 , 0.03561978, 
        0.05527796,0.09712188, 0.20376833, 0.39173692, 1.        
    ])
    
    # Case 1a: Passing 'AFR'
    result_1a = damage_factor_builtup(x, 'AFR')
    assert test_outcomes(result_1a, expected_africa)
    
    # Case 1b: Passing 'MENA'
    result_1b = damage_factor_builtup(x, 'MENA')
    assert test_outcomes(result_1b, expected_africa)    


    ## Case 2: Test with sample values for Asian region
    expected_asia = np.array([
        0.0025538 , 0.01040312, 0.0415447 , 0.07877379, 
        0.11401381,0.17890422, 0.31396794, 0.50474888, 1.        
    ])
    
    # Case 2a: Passing 'EAP'
    result_2a = damage_factor_builtup(x, 'EAP')
    assert test_outcomes(result_2a, expected_asia)
        
    # Case 2b: Passing 'SAR'
    result_2b = damage_factor_builtup(x, 'SAR')
    assert test_outcomes(result_2b, expected_asia)
    
    # Case 2c: Passing 'ECA'
    result_2c = damage_factor_builtup(x, 'ECA')
    assert test_outcomes(result_2c, expected_asia)
    
    
    # TODO: Test LAC 
    
    
    # TODO: Test GLOBAL 
    
    
    
# TODO: Test damage_factor_agri
