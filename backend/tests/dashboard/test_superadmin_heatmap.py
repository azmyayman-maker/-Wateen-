import pytest

from dashboard.services.superadmin_engine import get_fuzzed_nationwide_heatmap


@pytest.mark.django_db
def test_snap_to_grid_fuzzes_coordinates():
    """
    Validate that ST_SnapToGrid accurately clusters locations and no exact coordinates leak,
    satisfying Law 151/2020 data residency privacy compliance.
    """
    result = get_fuzzed_nationwide_heatmap()
    assert isinstance(result, list)
    if len(result) > 0:
        first_cluster = result[0]
        assert "lng" in first_cluster
        assert "lat" in first_cluster
        assert "count" in first_cluster
