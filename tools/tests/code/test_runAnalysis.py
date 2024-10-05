import pytest
import pandas as pd
from tools.code.runAnalysis import chunks, result_df_reorder_columns


def test_chunks():
    
    # Test Case 1
    iterable = list(range(1,8))
    result = list(chunks(iterable, 3))
    expected = [[1,2,3], [4,5,6], [7]]
    assert result == expected
    
    # Test Case 2
    iterable = list(range(1,7))
    result = list(chunks(iterable, 2))
    expected = [[1,2], [3,4], [5,6]]
    assert result == expected
    

def test_result_df_reorder_columns():
    
    df = pd.DataFrame({
            "geometry": ["geom1", "geom2"],
            "ADM1_code": [1, 2],
            "ADM1_name": ["Region1", "Region2"],
            "ADM1_Category1": ["ADM1a", "ADM1b"],
            "RP10_Category1_exp": [100, 200],
            "RP10_Category1_imp": [50, 100],
            "RP20_Category1_exp": [150, 250],
            "RP20_Category1_imp": [75, 125],
    })
    
    # Test Case 1: Reorder column functions of type analysis
    expected_df = pd.DataFrame({
       "ADM1_code": [1, 2],
       "ADM1_name": ["Region1", "Region2"],
       "ADM1_Category1": ["ADM1a", "ADM1b"],
        "RP10_Category1_exp": [100, 200],
        "RP20_Category1_exp": [150, 250],
        "RP10_Category1_imp": [50, 100],
        "RP20_Category1_imp": [75, 125],
        "geometry": ["geom1", "geom2"]
    })
    
    result_df = result_df_reorder_columns(
        df, RPs=[10, 20], analysis_type='Function', exp_cat='Category1', 
        adm_level=1, all_adm_codes=['ADM1_code'], all_adm_names=['ADM1_name']
    )
    
    pd.testing.assert_frame_equal(result_df, expected_df)
    
    
    # Test Case 2: No reordering becauase analysis_type is not function
    result2_df = result_df_reorder_columns(
        df, RPs=[10, 20], analysis_type='Classes', exp_cat='Category1',
        adm_level=1, all_adm_codes=['ADM1_code'], all_adm_names=['ADM1_name']
    )
    
    pd.testing.assert_frame_equal(result2_df, df)
    
    # Test Case 3: Error is through because of missing column 
    df_missing_col = df.drop(columns=['RP20_Category1_exp'])
    with pytest.raises(KeyError) as exc_inf:
        _ = result_df_reorder_columns(
            df_missing_col, RPs=[10, 20], analysis_type='Function', exp_cat='Category1',
            adm_level=1, all_adm_codes=['ADM1_code'], all_adm_names=['ADM1_name']
        )
    assert str(exc_inf.value) == '"[\'RP20_Category1_exp\'] not in index"'
