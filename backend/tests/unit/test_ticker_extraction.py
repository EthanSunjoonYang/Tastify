from app.utils.tickers import extract_tickers, is_known_ticker


def test_dollar_prefixed_ticker_is_extracted():
    assert extract_tickers("$AAPL is looking strong today") == {"AAPL"}


def test_bare_all_caps_ticker_is_extracted():
    assert extract_tickers("GME to the moon") == {"GME"}


def test_multiple_tickers_in_one_post():
    assert extract_tickers("Comparing $AAPL vs TSLA vs GME this week") == {"AAPL", "TSLA", "GME"}


def test_common_word_that_is_also_a_ticker_is_dropped_when_bare():
    # "ARE" (Alexandria Real Estate) and "IT" (Gartner) are real tickers, but
    # bare mentions in ordinary sentences are overwhelmingly the English word.
    assert extract_tickers("These stocks are cheap and IT infrastructure is booming") == set()


def test_dollar_prefix_bypasses_stopword_filter():
    # A $-prefixed mention is unambiguous, so it should count even for stopword-like symbols.
    assert extract_tickers("Loading up on $ARE ahead of earnings") == {"ARE"}


def test_unknown_symbol_is_not_extracted():
    assert extract_tickers("$ZZZZZ is not a real ticker") == set()
    assert extract_tickers("XYZQQ mentioned here") == set()


def test_lowercase_dollar_ticker_is_normalized_to_uppercase():
    assert extract_tickers("thinking about $aapl calls") == {"AAPL"}


def test_is_known_ticker():
    assert is_known_ticker("AAPL") is True
    assert is_known_ticker("aapl") is True
    assert is_known_ticker("ZZZZZ") is False
