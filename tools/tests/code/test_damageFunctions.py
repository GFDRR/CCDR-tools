from tools.code.damageFunctions import FL_mortality_factor, FL_damage_factor_builtup, FL_damage_factor_agri
import numpy as np
import pytest


def compare_outcomes(x,y):
    return np.allclose(x, y, rtol=1e-5)


def test_mortality_factor():
    
    # Case 1: Typical input values
    x = np.array([0, 10, 50, 100, 200])
    expected = np.array([0.00176976, 0.0020376 , 0.00357871, 0.00722308, 0.02898486])    
    result = FL_mortality_factor(x)
    compare_outcomes(result, expected)
    
    # TODO
    # Case 2: Test edge cases
    
    # TODO
    # Case 3: Test that clipping to 0 and 1 works out 
    
    
    # Case 4: Failing with Invalid input types
    with pytest.raises(TypeError):
        FL_mortality_factor("invalid INPUT!")
    
    # Case 5: Failing with None passed
    with pytest.raises(TypeError):
        FL_mortality_factor()
        
    with pytest.raises(TypeError):
        FL_mortality_factor(None)


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
    result_1a = FL_damage_factor_builtup(x, 'AFR')
    assert test_outcomes(result_1a, expected_africa)
    
    # Case 1b: Passing 'MENA'
    result_1b = FL_damage_factor_builtup(x, 'MENA')
    assert test_outcomes(result_1b, expected_africa)    


    ## Case 2: Test with sample values for Asian region
    expected_asia = np.array([
        0.0025538 , 0.01040312, 0.0415447 , 0.07877379, 
        0.11401381,0.17890422, 0.31396794, 0.50474888, 1.        
    ])
    
    # Case 2a: Passing 'EAP'
    result_2a = FL_damage_factor_builtup(x, 'EAP')
    assert test_outcomes(result_2a, expected_asia)
        
    # Case 2b: Passing 'SAR'
    result_2b = FL_damage_factor_builtup(x, 'SAR')
    assert test_outcomes(result_2b, expected_asia)
    
    # Case 2c: Passing 'ECA'
    result_2c = FL_damage_factor_builtup(x, 'ECA')
    assert test_outcomes(result_2c, expected_asia)
    
    
    # Case 3: Test with sample values for LAC region
    expected_lac = np.array([
        0.00149058, 0.00387057, 0.02788907, 0.07329972, 
        0.12665801, 0.23903597, 0.47772589, 0.73745742, 1.
    ])
    
    # Only one LAC so far
    result_3 = FL_damage_factor_builtup(x, 'LCR')
    assert test_outcomes(result_3, expected_lac)
    
    
    # Case 4: Test with sample values for GLOBAL region 
    expected_global = np.array([
        0.        , 0.05400394, 0.12809041, 0.18346507,
        0.22516733,0.2893803 , 0.40031077, 0.54105391, 1.
    ])
    
    # Case 4a: Passing 'Other'
    result_4a = FL_damage_factor_builtup(x, 'Other')
    assert test_outcomes(result_4a, expected_global)
    
    # Case 4b: Passing another variable that is not in dict, should default to GLOBAL
    result_4b = FL_damage_factor_builtup(x, 'ANY_OTHER_REGION')
    assert test_outcomes(result_4b, expected_global)
    
    
def test_damage_factor_agri():
    
    # We will reuse this np array through the tests
    x = np.array([0, 1, 5, 10, 15, 25, 50, 100, 1000])

    # Case 1: Test AFRICA
    expected_africa = np.array([
        0.01417282, 0.01447255, 0.01860892, 0.02827435, 
        0.04179812,0.07796918, 0.2039562 , 0.50278286, 1.
    ])
    
    # Case 1a: Passing 'AFR'
    result_1a = FL_damage_factor_agri(x, 'AFR')
    assert compare_outcomes(result_1a, expected_africa)
    
    # Case 1b: Passing 'MENA'
    result_1b = FL_damage_factor_agri(x, 'MENA')
    assert compare_outcomes(result_1b, expected_africa)
    
    
    # Case 2: Test ASIA
    expected_asia = np.array([
        0.        , 0.00426   , 0.02108523, 0.04164555, 
        0.06170034,0.1003661 , 0.1893709 , 0.34022844, 1.
    ])
    
    # Case 2a: Passing 'EAP'
    result_2a = FL_damage_factor_agri(x, 'EAP')
    assert compare_outcomes(result_2a, expected_asia)
    
    # Case 2b: Passing 'SAR'
    result_2b = FL_damage_factor_agri(x, 'SAR')
    assert compare_outcomes(result_2b, expected_asia)
    
    # Case 2c: Passing 'ECA'
    result_2c = FL_damage_factor_agri(x, 'ECA')
    assert compare_outcomes(result_2c, expected_asia)
    
    
    # Case 3: Test with sample values for LAC region
    expected_lac = np.array([
        0.01855393, 0.03442536, 0.07164524, 0.10688757, 
        0.13687177,0.18811284, 0.28907636, 0.43531503, 1.
    ])
    
    # Only one LAC so far
    result_3 = FL_damage_factor_agri(x, 'LCR')
    assert compare_outcomes(result_3, expected_lac)
    
    
    # Case 4: Test with sample values for GLOBAL region 
    expected_global = np.array([
        0.        , 0.        , 0.015485  , 0.03943019, 
        0.06547371, 0.11976183, 0.25131424, 0.46160653, 1.
    ])
    
    # Case 4a: Passing 'Other'
    result_4a = FL_damage_factor_agri(x, 'Other')
    assert compare_outcomes(result_4a, expected_global)
    
    # Case 4b: Passing another variable that is not in dict, should default to GLOBAL
    result_4b = FL_damage_factor_agri(x, 'ANY_OTHER_REGION')
    assert compare_outcomes(result_4b, expected_global)


#TODO: Test TC damage factor