import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

# Preserves the original plan's relative trust in genre vs. artist (0.4 : 0.35),
# renormalized to sum to 1 after dropping the audio-based "vibe" pillar (0.25)
# that Spotify's API changes made impossible to compute.
ERA_WEIGHT = 8 / 15
ARTIST_WEIGHT = 7 / 15

SHARED_ARTISTS_LIMIT = 25
UNIQUE_ARTISTS_LIMIT = 10


def compute_jaccard_index(ids_a: set[str], ids_b: set[str]) -> float:
    union = ids_a | ids_b
    if not union:
        # Both empty: there's no evidence of overlap, so treat it as 0 rather
        # than the vacuous "1.0 = identical" some libraries default to.
        return 0.0
    return len(ids_a & ids_b) / len(union)


def compute_cosine_similarity(vec_a: dict[str, float], vec_b: dict[str, float]) -> float:
    keys = sorted(set(vec_a) | set(vec_b))
    if not keys:
        return 0.0
    a = np.array([[vec_a.get(k, 0.0) for k in keys]])
    b = np.array([[vec_b.get(k, 0.0) for k in keys]])
    if not a.any() or not b.any():
        return 0.0
    return float(cosine_similarity(a, b)[0][0])


def compute_overall_score(era_score: float, artist_score: float) -> float:
    return ERA_WEIGHT * era_score + ARTIST_WEIGHT * artist_score


def compute_shared_artists(
    weights_a: dict[str, float],
    names_a: dict[str, str],
    images_a: dict[str, str],
    weights_b: dict[str, float],
    names_b: dict[str, str],
    images_b: dict[str, str],
) -> list[dict]:
    shared = [
        {
            "artist_id": artist_id,
            "name": names_a.get(artist_id) or names_b.get(artist_id, ""),
            "image_url": images_a.get(artist_id) or images_b.get(artist_id, ""),
            "weight_a": weights_a[artist_id],
            "weight_b": weights_b[artist_id],
            "combined_weight": weights_a[artist_id] + weights_b[artist_id],
        }
        for artist_id in set(weights_a) & set(weights_b)
    ]
    shared.sort(key=lambda entry: -entry["combined_weight"])
    return shared[:SHARED_ARTISTS_LIMIT]


def compute_unique_artists(
    weights_source: dict[str, float],
    names_source: dict[str, str],
    images_source: dict[str, str],
    weights_other: dict[str, float],
) -> list[dict]:
    unique = [
        {
            "artist_id": artist_id,
            "name": names_source.get(artist_id, ""),
            "image_url": images_source.get(artist_id, ""),
            "weight": weight,
        }
        for artist_id, weight in weights_source.items()
        if artist_id not in weights_other
    ]
    unique.sort(key=lambda entry: -entry["weight"])
    return unique[:UNIQUE_ARTISTS_LIMIT]


def _decade_sort_key(decade: str) -> int:
    return int(decade[:-1])


def compute_era_gaps(era_a: dict[str, float], era_b: dict[str, float]) -> dict[str, list[str]]:
    return {
        "only_in_a": sorted(set(era_a) - set(era_b), key=_decade_sort_key),
        "only_in_b": sorted(set(era_b) - set(era_a), key=_decade_sort_key),
    }


def compute_era_breakdown(era_a: dict[str, float], era_b: dict[str, float]) -> list[dict]:
    decades = sorted(set(era_a) | set(era_b), key=_decade_sort_key)
    return [
        {"decade": decade, "user_a": era_a.get(decade, 0.0), "user_b": era_b.get(decade, 0.0)}
        for decade in decades
    ]
