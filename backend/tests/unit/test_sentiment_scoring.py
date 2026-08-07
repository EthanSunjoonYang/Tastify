import math
from datetime import UTC, datetime

from app.models.reddit_post import RedditPost
from app.models.ticker import Ticker
from app.services.sentiment import (
    analyze_text,
    score_post,
    score_unscored_posts,
    weighted_score,
)


def test_analyze_text_scores_positive_text_positively():
    result = analyze_text("AAPL is crushing it, best stock ever, so bullish!")
    assert result["compound"] > 0


def test_analyze_text_scores_negative_text_negatively():
    result = analyze_text("This company is a disaster, terrible earnings, avoid at all costs")
    assert result["compound"] < 0


def test_weighted_score_formula():
    assert weighted_score(0.5, upvotes=99, num_comments=0) == 0.5 * math.log(100)
    assert weighted_score(-0.4, upvotes=0, num_comments=0) == -0.4 * math.log(1)


def _make_post(**overrides) -> RedditPost:
    defaults = dict(
        reddit_id="p1",
        subreddit="wallstreetbets",
        title="default title",
        body=None,
        score=10,
        num_comments=5,
        created_utc=datetime.now(UTC),
    )
    defaults.update(overrides)
    return RedditPost(**defaults)


def test_score_post_creates_one_row_per_mentioned_ticker(db_session):
    post = _make_post(title="Comparing $AAPL vs TSLA today")
    db_session.add(post)
    db_session.commit()

    scores = score_post(db_session, post)

    assert len(scores) == 2
    symbols = {
        db_session.get(Ticker, s.ticker_id).symbol for s in scores
    }
    assert symbols == {"AAPL", "TSLA"}
    # Same underlying text -> identical sentiment components across fanned-out tickers.
    assert scores[0].compound_score == scores[1].compound_score
    assert scores[0].weighted_score == scores[1].weighted_score


def test_score_post_skips_posts_with_no_ticker_mentions(db_session):
    post = _make_post(reddit_id="p2", title="just a general market discussion")
    db_session.add(post)
    db_session.commit()

    scores = score_post(db_session, post)

    assert scores == []


def test_score_unscored_posts_skips_already_scored(db_session):
    scored_post = _make_post(reddit_id="already-scored", title="$AAPL earnings beat")
    unscored_post = _make_post(reddit_id="not-yet-scored", title="$TSLA delivery numbers")
    db_session.add_all([scored_post, unscored_post])
    db_session.commit()

    score_post(db_session, scored_post)  # pre-score one of them

    new_scores = score_unscored_posts(db_session)

    assert len(new_scores) == 1
    assert new_scores[0].post_id == unscored_post.id
