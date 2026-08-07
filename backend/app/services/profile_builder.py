from collections import defaultdict

# medium_term (~6mo) is trusted most: it's stable enough to avoid overfitting to a
# recent binge, but recent enough to not anchor entirely on years-old taste.
RANGE_WEIGHTS = {"short_term": 0.2, "medium_term": 0.5, "long_term": 0.3}


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


def _normalize_to_max(scores: dict[str, float]) -> dict[str, float]:
    if not scores:
        return {}
    max_score = max(scores.values())
    return {key: value / max_score for key, value in scores.items()}


def compute_artist_weights(top_artists_by_range: dict[str, list[dict]]) -> dict[str, float]:
    return _normalize_to_max(_rank_weighted_scores(top_artists_by_range))


def compute_track_weights(top_tracks_by_range: dict[str, list[dict]]) -> dict[str, float]:
    return _normalize_to_max(_rank_weighted_scores(top_tracks_by_range))


def compute_artist_names(top_artists_by_range: dict[str, list[dict]]) -> dict[str, str]:
    names: dict[str, str] = {}
    for artists in top_artists_by_range.values():
        for artist in artists:
            names[artist["id"]] = artist.get("name", "")
    return names


def compute_top_track_pool(top_tracks_by_range: dict[str, list[dict]]) -> list[str]:
    scores = _rank_weighted_scores(top_tracks_by_range)
    return [track_id for track_id, _ in sorted(scores.items(), key=lambda kv: -kv[1])]


def _decade_bucket(release_date: str) -> str | None:
    year_str = release_date[:4]
    if not year_str.isdigit():
        return None
    return f"{(int(year_str) // 10) * 10}s"


def compute_track_meta(top_tracks_by_range: dict[str, list[dict]]) -> dict[str, dict]:
    """Per-track name/artists/decade, cached so playlist generation never needs a
    second round of Spotify API calls to know what a track_id actually is."""
    meta: dict[str, dict] = {}
    for tracks in top_tracks_by_range.values():
        for track in tracks:
            release_date = track.get("album", {}).get("release_date", "")
            meta[track["id"]] = {
                "name": track.get("name", ""),
                "artist_ids": [artist["id"] for artist in track.get("artists", [])],
                "decade": _decade_bucket(release_date),
            }
    return meta


def compute_era_vector(
    top_tracks_by_range: dict[str, list[dict]], track_weights: dict[str, float]
) -> dict[str, float]:
    """Decade distribution of a user's top tracks -- the genre-vector replacement.

    Spotify stopped populating genre tags on artist/album objects platform-wide
    (verified empty across the top-artists, artist, and album endpoints), so this
    swaps the feature space to release-year decade, which Spotify still reliably
    returns on every track's album. Same cosine-similarity comparison downstream,
    just a different axis: "what era do you listen to" instead of "what genre."
    """
    track_decades: dict[str, str] = {}
    for tracks in top_tracks_by_range.values():
        for track in tracks:
            release_date = track.get("album", {}).get("release_date", "")
            decade = _decade_bucket(release_date)
            if decade is not None:
                track_decades[track["id"]] = decade

    decade_totals: dict[str, float] = defaultdict(float)
    for track_id, weight in track_weights.items():
        decade = track_decades.get(track_id)
        if decade is not None:
            decade_totals[decade] += weight

    total = sum(decade_totals.values())
    if total == 0:
        return {}
    return {decade: value / total for decade, value in decade_totals.items()}
