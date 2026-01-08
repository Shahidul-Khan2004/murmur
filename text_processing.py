from nltk.sentiment.vader import SentimentIntensityAnalyzer
from functools import lru_cache

@lru_cache(maxsize=1)
def get_analyzer():
    try:
        return SentimentIntensityAnalyzer()
    except LookupError:
        import nltk
        nltk.download("vader_lexicon")
        return SentimentIntensityAnalyzer()


def analyze_sentiment(text: str) -> str:
    """
    Analyze the sentiment of the given text and return a sentiment label.

    Parameters
    ----------
    text : str
        The input text to analyze.

    Returns
    -------
    str
        'Positive', 'Negative', or 'Neutral' based on sentiment analysis.
    """
    analyzer = get_analyzer()
    score = analyzer.polarity_scores(text)
    if score["compound"] >= 0.25:
        return "Positive"
    elif score["compound"] <= -0.25:
        return "Negative"
    else:
        return "Neutral"
