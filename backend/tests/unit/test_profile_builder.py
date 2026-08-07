import pytest

from app.services.profile_builder import (
    compute_artist_names,
    compute_artist_weights,
    compute_era_vector,
    compute_top_track_pool,
    compute_track_meta,
    compute_track_weights,
)


def test_compute_artist_weights_combines_ranges_and_normalizes_to_top_artist():
    top_artists_by_range = {
        "short_term": [{"id": "a2"}],
        "medium_term": [{"id": "a1"}, {"id": "a2"}],
        "long_term": [],
    }

    weights = compute_artist_weights(top_artists_by_range)

    # a1: medium_term rank0 -> 0.5/1 = 0.5 (the max, so normalizes to 1.0)
    # a2: short_term rank0 -> 0.2/1 = 0.2, medium_term rank1 -> 0.5/2 = 0.25, sum 0.45
    assert weights["a1"] == pytest.approx(1.0)
    assert weights["a2"] == pytest.approx(0.45 / 0.5)


def test_compute_artist_weights_empty_input():
    assert compute_artist_weights({"short_term": [], "medium_term": [], "long_term": []}) == {}


def test_compute_artist_names_maps_id_to_name_across_ranges():
    top_artists_by_range = {
        "short_term": [{"id": "a1", "name": "Artist One"}],
        "medium_term": [{"id": "a1", "name": "Artist One"}, {"id": "a2", "name": "Artist Two"}],
        "long_term": [],
    }

    assert compute_artist_names(top_artists_by_range) == {
        "a1": "Artist One",
        "a2": "Artist Two",
    }


def test_compute_top_track_pool_orders_by_combined_weight_descending():
    top_tracks_by_range = {
        "short_term": [{"id": "t1"}, {"id": "t2"}],
        "medium_term": [{"id": "t2"}, {"id": "t3"}],
        "long_term": [{"id": "t3"}],
    }

    # t1: 0.2/1 = 0.2
    # t2: 0.2/2 + 0.5/1 = 0.6
    # t3: 0.5/2 + 0.3/1 = 0.55
    assert compute_top_track_pool(top_tracks_by_range) == ["t2", "t3", "t1"]


def test_compute_era_vector_buckets_by_decade_and_normalizes_to_one():
    top_tracks_by_range = {
        "short_term": [{"id": "t2", "album": {"release_date": "2015-06-01"}}],
        "medium_term": [
            {"id": "t1", "album": {"release_date": "2005-01-01"}},
            {"id": "t2", "album": {"release_date": "2015-06-01"}},
        ],
        "long_term": [],
    }
    track_weights = compute_track_weights(top_tracks_by_range)

    era_vector = compute_era_vector(top_tracks_by_range, track_weights)

    # t1 -> 2000s at weight 1.0, t2 -> 2010s at weight 0.9 (same math as artist weights above)
    assert era_vector["2000s"] == pytest.approx(1.0 / 1.9)
    assert era_vector["2010s"] == pytest.approx(0.9 / 1.9)
    assert sum(era_vector.values()) == pytest.approx(1.0)


def test_compute_era_vector_handles_year_only_precision():
    top_tracks_by_range = {
        "medium_term": [{"id": "t1", "album": {"release_date": "1998"}}],
        "short_term": [],
        "long_term": [],
    }
    track_weights = compute_track_weights(top_tracks_by_range)

    era_vector = compute_era_vector(top_tracks_by_range, track_weights)

    assert era_vector == {"1990s": pytest.approx(1.0)}


def test_compute_era_vector_no_tracks_returns_empty():
    assert compute_era_vector({}, {}) == {}


def test_compute_era_vector_missing_release_date_is_skipped():
    top_tracks_by_range = {
        "medium_term": [{"id": "t1", "album": {"release_date": ""}}],
        "short_term": [],
        "long_term": [],
    }
    track_weights = compute_track_weights(top_tracks_by_range)

    assert compute_era_vector(top_tracks_by_range, track_weights) == {}


def test_compute_track_meta_extracts_name_artists_and_decade():
    top_tracks_by_range = {
        "medium_term": [
            {
                "id": "t1",
                "name": "Song One",
                "artists": [{"id": "a1"}, {"id": "a2"}],
                "album": {"release_date": "2015-06-01"},
            }
        ],
        "short_term": [],
        "long_term": [],
    }

    assert compute_track_meta(top_tracks_by_range) == {
        "t1": {"name": "Song One", "artist_ids": ["a1", "a2"], "decade": "2010s"}
    }
