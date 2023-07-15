import nltk
import spacy as sp
from nltk.sentiment.vader import SentimentIntensityAnalyzer

PARSER_KEY = "SentimentAnalyzer_v1"


class SentimentAnalyzer:
    def __init__(self):
        # Download the NLTK VADER lexicon
        nltk.download('vader_lexicon')

        # Download en_core_web_sm
        try:
            sp.load('en_core_web_sm')
        except OSError:
            print("Downloading 'en_core_web_sm' model...")
            sp.cli.download('en_core_web_sm')

        # Initialize spaCy and the VADER sentiment analyzer
        self.nlp = sp.load('en_core_web_sm')
        self.sia = SentimentIntensityAnalyzer()

    def get_sentiment(self, text):
        doc = self.nlp(text)
        sentences = [sent.text.strip() for sent in doc.sents]
        sentiment_scores = [self.sia.polarity_scores(sentence)['compound'] for sentence in sentences]
        average_score = sum(sentiment_scores) / len(sentiment_scores)
        return average_score
        # if average_score >= 0.05:
        #     return "Positive"
        # elif average_score <= -0.05:
        #     return "Negative"
        # else:
        #     return "Neutral"


if __name__ == '__main__':
    # Example usage
    # sample = "It had a great storyline and fantastic acting but I hate this"
    # text = "I hate this"
    # sample = "All of this was borrowed money with a very high interest rate. "
    sample = "Cointelegraph News https://cointelegraph.com/news/riot-platforms-add-bitcoin-miners-ahead-of-2024-halving"

    analyzer = SentimentAnalyzer()
    sentiment = analyzer.get_sentiment(sample)
    print(sentiment)
