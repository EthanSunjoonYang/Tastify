import pytest

from app.services.profile_builder import (
    compute_artist_weights,
    compute_audio_profile,
    compute_genre_vector,
    compute_top_track_pool,
)


def test_compute_artist_weights_combines_ranges_and_normalizes_to_top_artist():
    top_artists_by_range = {
        "short_term": [{"id": "a2", "genres": ["pop"]}],
        "medium_term": [{"id": "a1", "genres": ["rock"]}, {"id": "a2", "genres": ["pop"]}],
        "long_term": [],
    }

    weights = compute_artist_weights(top_artists_by_range)

    # a1: medium_term rank0 -> 0.5/1 = 0.5 (the max, so normalizes to 1.0)
    # a2: short_term rank0 -> 0.2/1 = 0.2, medium_term rank1 -> 0.5/2 = 0.25, sum 0.45
    assert weights["a1"] == pytest.approx(1.0)
    assert weights["a2"] == pytest.approx(0.45 / 0.5)


def test_compute_artist_weights_empty_input():
    assert compute_artist_weights({"short_term": [], "medium_term": [], "long_term": []}) == {}


def test_compute_genre_vector_sums_weights_per_genre_and_normalizes_to_one():
    top_artists_by_range = {
        "short_term": [{"id": "a2", "genres": ["pop"]}],
        "medium_term": [{"id": "a1", "genres": ["rock"]}, {"id": "a2", "genres": ["pop"]}],
        "long_term": [],
    }
    artist_weights = compute_artist_weights(top_artists_by_range)

    genre_vector = compute_genre_vector(top_artists_by_range, artist_weights)

    assert genre_vector["rock"] == pytest.approx(1.0 / 1.9)
    assert genre_vector["pop"] == pytest.approx(0.9 / 1.9)
    assert sum(genre_vector.values()) == pytest.approx(1.0)


def test_compute_genre_vector_no_artists_returns_empty():
    assert compute_genre_vector({}, {}) == {}


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


def test_compute_audio_profile_averages_and_dedupes_by_track_id():
    audio_features = [
        {
            "id": "t1",
            "danceability": 0.5,
            "energy": 0.6,
            "valence": 0.7,
            "tempo": 120,
            "acousticness": 0.1,
        },
        {
            "id": "t2",
            "danceability": 0.7,
            "energy": 0.8,
            "valence": 0.5,
            "tempo": 100,
            "acousticness": 0.3,
        },
        # duplicate id for t1 must count once toward the average, not three times
        {
            "id": "t1",
            "danceability": 0.9,
            "energy": 0.9,
            "valence": 0.9,
            "tempo": 200,
            "acousticness": 0.9,
        },
    ]

    profile = compute_audio_profile(audio_features)

    # dedup keeps the last occurrence of a repeated id, so t1 contributes its
    # second entry (0.9/0.9/0.9/200/0.9), averaged with t2
    assert profile["danceability"] == pytest.approx(0.8)
    assert profile["energy"] == pytest.approx(0.85)
    assert profile["valence"] == pytest.approx(0.7)
    assert profile["tempo"] == pytest.approx(150)
    assert profile["acousticness"] == pytest.approx(0.6)


def test_compute_audio_profile_empty_input_returns_zeros():
    profile = compute_audio_profile([])

    assert profile == {
        "danceability": 0.0,
        "energy": 0.0,
        "valence": 0.0,
        "tempo": 0.0,
        "acousticness": 0.0,
    }
