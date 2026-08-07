import pytest

from app.services.comparison_engine import (
    ARTIST_WEIGHT,
    ERA_WEIGHT,
    compute_cosine_similarity,
    compute_era_breakdown,
    compute_era_gaps,
    compute_jaccard_index,
    compute_overall_score,
    compute_shared_artists,
    compute_unique_artists,
)


def test_jaccard_index_partial_overlap():
    # shared: {b, c}; union: {a, b, c, d} -> 2/4
    assert compute_jaccard_index({"a", "b", "c"}, {"b", "c", "d"}) == pytest.approx(0.5)


def test_jaccard_index_identical_sets_is_one():
    assert compute_jaccard_index({"a", "b"}, {"a", "b"}) == pytest.approx(1.0)


def test_jaccard_index_no_overlap_is_zero():
    assert compute_jaccard_index({"a"}, {"b"}) == pytest.approx(0.0)


def test_jaccard_index_both_empty_is_zero_not_one():
    assert compute_jaccard_index(set(), set()) == 0.0


def test_cosine_similarity_identical_vectors_is_one():
    vec = {"2010s": 0.6, "2020s": 0.4}
    assert compute_cosine_similarity(vec, vec) == pytest.approx(1.0)


def test_cosine_similarity_disjoint_axes_is_zero():
    assert compute_cosine_similarity({"2010s": 1.0}, {"2020s": 1.0}) == pytest.approx(0.0)


def test_cosine_similarity_empty_vector_is_zero():
    assert compute_cosine_similarity({}, {"2010s": 1.0}) == 0.0
    assert compute_cosine_similarity({}, {}) == 0.0


def test_overall_score_weights_sum_to_one():
    assert ERA_WEIGHT + ARTIST_WEIGHT == pytest.approx(1.0)


def test_overall_score_is_weighted_average():
    # 8/15 * 0.8 + 7/15 * 0.4 = 0.4267 + 0.1867 = 0.6133
    assert compute_overall_score(era_score=0.8, artist_score=0.4) == pytest.approx(
        ERA_WEIGHT * 0.8 + ARTIST_WEIGHT * 0.4
    )


def test_overall_score_identical_taste_is_one():
    assert compute_overall_score(era_score=1.0, artist_score=1.0) == pytest.approx(1.0)


def test_shared_artists_only_includes_common_ids_sorted_by_combined_weight():
    weights_a = {"a1": 0.9, "a2": 0.3}
    weights_b = {"a1": 0.5, "a3": 0.2}
    names_a = {"a1": "Artist One", "a2": "Artist Two"}
    names_b = {"a1": "Artist One", "a3": "Artist Three"}
    images_a = {"a1": "https://img/a1.jpg", "a2": "https://img/a2.jpg"}
    images_b = {"a1": "https://img/a1.jpg", "a3": "https://img/a3.jpg"}

    shared = compute_shared_artists(weights_a, names_a, images_a, weights_b, names_b, images_b)

    assert shared == [
        {
            "artist_id": "a1",
            "name": "Artist One",
            "image_url": "https://img/a1.jpg",
            "weight_a": 0.9,
            "weight_b": 0.5,
            "combined_weight": pytest.approx(1.4),
        }
    ]


def test_unique_artists_excludes_ids_present_in_other():
    weights_source = {"a1": 0.9, "a2": 0.3}
    names_source = {"a1": "Artist One", "a2": "Artist Two"}
    images_source = {"a1": "https://img/a1.jpg", "a2": "https://img/a2.jpg"}
    weights_other = {"a1": 0.5}

    unique = compute_unique_artists(weights_source, names_source, images_source, weights_other)

    assert unique == [
        {
            "artist_id": "a2",
            "name": "Artist Two",
            "image_url": "https://img/a2.jpg",
            "weight": 0.3,
        }
    ]


def test_era_gaps_finds_decades_exclusive_to_each_side():
    era_a = {"2000s": 0.5, "2010s": 0.5}
    era_b = {"2010s": 1.0, "2020s": 0.3}

    gaps = compute_era_gaps(era_a, era_b)

    assert gaps == {"only_in_a": ["2000s"], "only_in_b": ["2020s"]}


def test_era_breakdown_fills_zero_for_missing_side_and_sorts_chronologically():
    era_a = {"2010s": 0.6, "1990s": 0.4}
    era_b = {"2010s": 0.3, "2020s": 0.7}

    breakdown = compute_era_breakdown(era_a, era_b)

    assert breakdown == [
        {"decade": "1990s", "user_a": 0.4, "user_b": 0.0},
        {"decade": "2010s", "user_a": 0.6, "user_b": 0.3},
        {"decade": "2020s", "user_a": 0.0, "user_b": 0.7},
    ]
