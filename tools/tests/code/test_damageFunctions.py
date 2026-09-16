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

    # NOTE: expected_* arrays below were regenerated against a refit of these
    # curves directly from the raw Huizinga et al. (2017) JRC data points
    # (previously hand-interpolated, with a confirmed bug in the AFRICA
    # branch - see damageFunctions.py). "Built-up" is now a weighted
    # composite of Residential/Commercial/Industrial rather than Residential
    # alone, and GLOBAL is refit from JRC's own Europe+NorthAmerica+Oceania
    # curves (the countries WB_REGION 'Other' actually represents) instead of
    # unsourced coefficients. These are deliberate, verified changes, not
    # regressions - see CHANGES_1.0.md for the full writeup and R^2 values.

    ## Case 1: Test with sample values for African region
    expected_africa = np.array([
        0.00413358, 0.00545347, 0.01455462, 0.02928794,
        0.04597354, 0.08251679, 0.1798563 , 0.3616008 , 1.
    ])

    # Case 1a: Passing 'AFR'
    result_1a = FL_damage_factor_builtup(x, 'AFR')
    assert test_outcomes(result_1a, expected_africa)

    # Case 1b: Passing 'MENA'
    result_1b = FL_damage_factor_builtup(x, 'MENA')
    assert test_outcomes(result_1b, expected_africa)


    ## Case 2: Test with sample values for Asian region
    expected_asia = np.array([
        0.00206518, 0.00939536, 0.039729  , 0.07673669,
        0.11211503, 0.17773604, 0.31511456, 0.508889  , 1.
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
        0.00088108, 0.00336635, 0.03019631, 0.0822553 ,
        0.14359915, 0.27089763, 0.52680933, 0.778599  , 1.
    ])

    # Only one LAC so far
    result_3 = FL_damage_factor_builtup(x, 'LCR')
    assert test_outcomes(result_3, expected_lac)


    # Case 4: Test with sample values for GLOBAL region
    # (covers the countries WB_REGION 'Other' maps to: North America, Japan,
    # Korea, Australia, New Zealand, and non-EU Europe - see wb_to_region and
    # resolve_flood_region in common.py)
    expected_global = np.array([
        0.05053091, 0.06111026, 0.09509242, 0.13182592,
        0.16492796, 0.22365844, 0.34192276, 0.5083705 , 1.
    ])

    # Case 4a: Passing 'Other'
    result_4a = FL_damage_factor_builtup(x, 'Other')
    assert test_outcomes(result_4a, expected_global)

    # Case 4b: Passing another variable that is not in dict, should default to GLOBAL
    result_4b = FL_damage_factor_builtup(x, 'ANY_OTHER_REGION')
    assert test_outcomes(result_4b, expected_global)


def test_damage_factor_builtup_europe():
    # EUROPE is a new bucket (see common.eu_country_codes /
    # resolve_flood_region): FL_damage_factor_builtup/agri accept the
    # already-resolved bucket name directly (not a raw WB code, since WB
    # region alone can't distinguish EU from non-EU countries within ECA or
    # 'Other') - fit from JRC's own dedicated EUROPE composite curve.
    x = np.array([0, 1, 5, 10, 15, 25, 50, 100, 1000])
    expected_europe = np.array([
        0.00210488, 0.00804591, 0.02892196, 0.05296326,
        0.07566142, 0.11815012, 0.21218097, 0.36502123, 1.
    ])
    result = FL_damage_factor_builtup(x, 'EUROPE')
    assert np.allclose(result, expected_europe, rtol=1e-5)


def test_damage_factor_agri():

    # We will reuse this np array through the tests
    x = np.array([0, 1, 5, 10, 15, 25, 50, 100, 1000])

    # NOTE: expected_* arrays below were regenerated against a refit of these
    # curves directly from the raw Huizinga et al. (2017) JRC data points -
    # see the equivalent note in test_damage_factor_builtup and
    # damageFunctions.py for details (in particular, a confirmed bug in the
    # AFRICA coefficients' exponent handling). LAC has no JRC agriculture
    # data at all, so it's now an intentional alias of GLOBAL rather than
    # fabricated coefficients - expected_lac and expected_global below are
    # therefore identical by design.

    # Case 1: Test AFRICA
    expected_africa = np.array([
        0.00111509, 0.00111835, 0.00144108, 0.00347896,
        0.008618  , 0.03269542, 0.1929778 , 0.63748567, 1.
    ])

    # Case 1a: Passing 'AFR'
    result_1a = FL_damage_factor_agri(x, 'AFR')
    assert compare_outcomes(result_1a, expected_africa)

    # Case 1b: Passing 'MENA'
    result_1b = FL_damage_factor_agri(x, 'MENA')
    assert compare_outcomes(result_1b, expected_africa)


    # Case 2: Test ASIA
    expected_asia = np.array([
        0.00016733, 0.00024901, 0.00186455, 0.00641389,
        0.01349865, 0.03441894, 0.1167987 , 0.3340983 , 1.
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


    # Case 3: Test with sample values for LAC region - no JRC source data,
    # intentionally identical to GLOBAL (see note above).
    expected_lac = np.array([
        0.        , 0.0022739 , 0.01705065, 0.0400118 ,
        0.06519115, 0.11810062, 0.24777308, 0.45759973, 1.
    ])

    # Only one LAC so far
    result_3 = FL_damage_factor_agri(x, 'LCR')
    assert compare_outcomes(result_3, expected_lac)


    # Case 4: Test with sample values for GLOBAL region
    expected_global = np.array([
        0.        , 0.0022739 , 0.01705065, 0.0400118 ,
        0.06519115, 0.11810062, 0.24777308, 0.45759973, 1.
    ])

    # Case 4a: Passing 'Other'
    result_4a = FL_damage_factor_agri(x, 'Other')
    assert compare_outcomes(result_4a, expected_global)

    # Case 4b: Passing another variable that is not in dict, should default to GLOBAL
    result_4b = FL_damage_factor_agri(x, 'ANY_OTHER_REGION')
    assert compare_outcomes(result_4b, expected_global)


def test_damage_factor_agri_europe():
    # EUROPE is a new bucket - JRC does publish agriculture data for Europe,
    # unlike LAC. See test_damage_factor_builtup_europe.
    x = np.array([0, 1, 5, 10, 15, 25, 50, 100, 1000])
    expected_europe = np.array([
        0.        , 0.00461234, 0.02900604, 0.06271231,
        0.09708726, 0.16424278, 0.31213802, 0.52389188, 1.
    ])
    result = FL_damage_factor_agri(x, 'EUROPE')
    assert np.allclose(np.array(result, dtype=float), expected_europe, rtol=1e-5)


#TODO: Test TC damage factor