import numpy as np
from shapely.geometry import Polygon, MultiPolygon

from tools.code.common import (
    unwrap_antimeridian_geometry, match_adm_level_layer, STORM_TO_1MIN_SUSTAINED_FACTOR
)
from tools.code.damageFunctions import TC_damage_factor_builtup


def test_unwrap_antimeridian_geometry_single_ring_crossing():
    # A single ring that crosses the seam (as EPSG:4326's own wrapping would
    # produce it): vertices jump from ~178 to ~-178.
    poly = Polygon([(178, -18), (-178, -18), (-178, -17), (178, -17)])
    result = unwrap_antimeridian_geometry(poly)
    xs = [x for x, y in result.exterior.coords]
    assert max(xs) - min(xs) < 10  # contiguous, not ~356 degrees wide
    assert result.is_valid


def test_unwrap_antimeridian_geometry_disconnected_parts():
    # A MultiPolygon whose parts sit entirely on one side or the other of
    # the seam, with no single ring ever crossing it - this is Fiji's real
    # shape (scattered islands), and the case a naive sequential per-ring
    # unwrap (numpy.unwrap-style) does NOT fix: confirmed against the real
    # Fiji ADM2 boundaries, where provinces like Lau came out with parts
    # left un-shifted and the overall bounding box still ~360 degrees wide.
    west_part = Polygon([(178, -18), (179, -18), (179, -17), (178, -17)])
    east_part = Polygon([(-179, -18), (-178.5, -18), (-178.5, -17.5), (-179, -17.5)])
    multi = MultiPolygon([west_part, east_part])

    result = unwrap_antimeridian_geometry(multi)
    all_xs = [x for part in result.geoms for x, y in part.exterior.coords]
    assert max(all_xs) - min(all_xs) < 10
    assert all(part.is_valid for part in result.geoms)
    # The east part (originally negative longitude) should have moved to
    # the 180+ range, not stayed at its wrapped [-180, 180] position.
    east_xs = [x for x, y in result.geoms[1].exterior.coords]
    assert min(east_xs) > 180


def test_match_adm_level_layer_ambiguous_returns_none():
    # Two layers both match ADM4 as a whole token - should not guess.
    layers = ['FJI_ADM4', 'FJI_ADM4_fix', 'FJI_ADM2']
    assert match_adm_level_layer(layers, 4) is None
    assert match_adm_level_layer(layers, 2) == 'FJI_ADM2'


def test_storm_to_1min_sustained_factor_matches_storm_documentation():
    # Bloemendaal et al. (2020): 1-min sustained = U10 / 0.8821.
    assert np.isclose(STORM_TO_1MIN_SUSTAINED_FACTOR, 1 / 0.8821, rtol=1e-9)
    # A raw STORM value of 50 m/s should convert to ~56.7 m/s.
    assert np.isclose(50 * STORM_TO_1MIN_SUSTAINED_FACTOR, 56.69, atol=0.01)


def test_storm_conversion_materially_changes_tc_damage():
    # Regression guard for the fix itself: applying the conversion before
    # evaluating the damage curve should noticeably raise damage relative to
    # feeding STORM's raw (unconverted) 10-minute mean value straight in -
    # confirmed against Fiji's Oceania curve (Vhalf=54.4): ~38% unconverted
    # vs. ~56% converted at a raw 50 m/s STORM value.
    x_raw = np.array([50.0])
    country = 'FJI'
    damage_raw = TC_damage_factor_builtup(x_raw, country)
    damage_converted = TC_damage_factor_builtup(x_raw * STORM_TO_1MIN_SUSTAINED_FACTOR, country)
    assert damage_converted[0] > damage_raw[0] + 0.15
