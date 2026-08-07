import math

from sqlalchemy import select
from sqlalchemy.orm import Session
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

from app.models.reddit_post import RedditPost
from app.models.sentiment_score import SentimentScore
from app.models.ticker import Ticker
from app.utils.tickers import extract_tickers

_analyzer = SentimentIntensityAnalyzer()


def analyze_text(text: str) -> dict[str, float]:
    """Raw VADER polarity scores for a piece of text."""
    return _analyzer.polarity_scores(text)


def weighted_score(compound_score: float, upvotes: int, num_comments: int) -> float:
    """Weight raw sentiment by engagement so a high-upvote post counts more than a
    zero-engagement post making the same claim."""
    return compound_score * math.log(max(upvotes, 0) + max(num_comments, 0) + 1)


def _get_or_create_ticker(db: Session, symbol: str) -> Ticker:
    ticker = db.execute(select(Ticker).where(Ticker.symbol == symbol)).scalar_one_or_none()
    if ticker is not None:
        return ticker
    ticker = Ticker(symbol=symbol, name=symbol)
    db.add(ticker)
    db.flush()
    return ticker


def score_post(db: Session, post: RedditPost) -> list[SentimentScore]:
    """Score a post's sentiment once and fan it out to every ticker it mentions."""
    text = post.title if not post.body else f"{post.title}\n{post.body}"
    tickers = extract_tickers(text)
    if not tickers:
        return []

    polarity = analyze_text(text)
    w_score = weighted_score(polarity["compound"], post.score, post.num_comments)

    created = []
    for symbol in tickers:
        ticker = _get_or_create_ticker(db, symbol)
        score = SentimentScore(
            ticker_id=ticker.id,
            post_id=post.id,
            compound_score=polarity["compound"],
            positive=polarity["pos"],
            negative=polarity["neg"],
            neutral=polarity["neu"],
            weighted_score=w_score,
        )
        db.add(score)
        created.append(score)

    db.commit()
    for score in created:
        db.refresh(score)
    return created


def score_unscored_posts(db: Session) -> list[SentimentScore]:
    """Score every RedditPost that doesn't have any SentimentScore rows yet."""
    scored_post_ids = select(SentimentScore.post_id).distinct()
    unscored_posts = (
        db.execute(select(RedditPost).where(RedditPost.id.not_in(scored_post_ids))).scalars().all()
    )

    all_scores: list[SentimentScore] = []
    for post in unscored_posts:
        all_scores.extend(score_post(db, post))
    return all_scores
