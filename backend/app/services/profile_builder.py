from collections import defaultdict

# medium_term (~6mo) is trusted most: it's stable enough to avoid overfitting to a
# recent binge, but recent enough to not anchor entirely on years-old taste.
RANGE_WEIGHTS = {"short_term": 0.2, "medium_term": 0.5, "long_term": 0.3}

AUDIO_FEATURE_KEYS = ("danceability", "energy", "valence", "tempo", "acousticness")


def _rank_weighted_scores(items_by_range: dict[str, list[dict]]) -> dict[str, float]:
    """Combine per-range rankings into one weighted score per item id.

    Within a range, rank 0 (top item) contributes the full range weight; rank r
    contributes range_weight / (r + 1). An item appearing in multiple ranges sums
    its contributions, so a consistently-ranked artist/track outweighs one that
    only spikes in a single range.
    """
    scores: dict[str, float] = defaultdict(float)
    for time_range, items in items_by_range.items():
        range_weight = RANGE_WEIGHTS[time_range]
        for rank, item in enumerate(items):
            scores[item["id"]] += range_weight / (rank + 1)
    return dict(scores)


def compute_artist_weights(top_artists_by_range: dict[str, list[dict]]) -> dict[str, float]:
    scores = _rank_weighted_scores(top_artists_by_range)
    if not scores:
        return {}
    max_score = max(scores.values())
    return {artist_id: score / max_score for artist_id, score in scores.items()}


def compute_genre_vector(
    top_artists_by_range: dict[str, list[dict]], artist_weights: dict[str, float]
) -> dict[str, float]:
    artist_genres: dict[str, list[str]] = {}
    for artists in top_artists_by_range.values():
        for artist in artists:
            artist_genres[artist["id"]] = artist.get("genres", [])

    genre_totals: dict[str, float] = defaultdict(float)
    for artist_id, weight in artist_weights.items():
        for genre in artist_genres.get(artist_id, []):
            genre_totals[genre] += weight

    total = sum(genre_totals.values())
    if total == 0:
        return {}
    return {genre: value / total for genre, value in genre_totals.items()}


def compute_top_track_pool(top_tracks_by_range: dict[str, list[dict]]) -> list[str]:
    scores = _rank_weighted_scores(top_tracks_by_range)
    return [track_id for track_id, _ in sorted(scores.items(), key=lambda kv: -kv[1])]


def compute_audio_profile(audio_features_list: list[dict]) -> dict[str, float]:
    deduped: dict[str, dict] = {f["id"]: f for f in audio_features_list if f.get("id")}
    if not deduped:
        return dict.fromkeys(AUDIO_FEATURE_KEYS, 0.0)

    count = len(deduped)
    return {
        key: sum(f[key] for f in deduped.values()) / count for key in AUDIO_FEATURE_KEYS
    }
