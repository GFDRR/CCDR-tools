import numpy as np
from shapely.geometry import Polygon, MultiPolygon

from tools.code.common import unwrap_antimeridian_geometry, match_adm_level_layer


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
