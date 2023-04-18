from flask import Flask, request, jsonify
import re
import tweepy
from tweepy import OAuthHandler
from textblob import TextBlob
from flask_cors import CORS
app = Flask(__name__)
CORS(app)
class TwitterClient(object):
    def __init__(self):
        consumer_key = '1ujnEu1YUlNpELrVdIKOKhoGO'
        consumer_secret = 'jitOtlZ727c3cKnpqTaRohsPckKGSEc6aTwNocTeqQXnPMfS2m'
        access_token = '1532967152005058560-EzTNhF5cTMwIFiHobePxDOfldAOSZ8'
        access_token_secret = 'xMjblKodYc8mhXHjtLriTpPJrdt2D32ejyGHoFOJrtjBJ'
        try:
            # create OAuthHandler object
            self.auth = OAuthHandler(consumer_key, consumer_secret)
            # set access token and secret
            self.auth.set_access_token(access_token, access_token_secret)
            # create tweepy API object to fetch tweets
            self.api = tweepy.API(self.auth)
        except:
            print("Error: Authentication Failed")

    def clean_tweet(self, tweet):
        return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweet).split())

    def get_tweet_sentiment(self, tweet):
        analysis = TextBlob(self.clean_tweet(tweet))
        if analysis.sentiment.polarity > 0:
            return 'positive'
        elif analysis.sentiment.polarity == 0:
            return 'neutral'
        else:
            return 'negative'

    def get_tweets(self, query, count=10):
        tweets = []

        try:
            fetched_tweets = self.api.search_tweets(q=query, count=count)

            for tweet in fetched_tweets:
                parsed_tweet = {}
                parsed_tweet['text'] = tweet.text
                parsed_tweet['sentiment'] = self.get_tweet_sentiment(tweet.text)
                parsed_tweet['id_str'] = tweet.id_str
                parsed_tweet['tweet_url'] = f"https://twitter.com/{tweet.user.screen_name}/status/{tweet.id_str}"
                if tweet.retweet_count > 0:
                    if parsed_tweet not in tweets:
                        tweets.append(parsed_tweet)
                else:
                    tweets.append(parsed_tweet)
            return tweets

        except tweepy.TweepError as e:
            print("Error : " + str(e))

@app.route('/')
def index():
    return "Hello, World!"

@app.route('/api/tweets', methods=['GET'])
def get_tweets():
    query = request.args.get('query')
    count = request.args.get('count', 10, type=int)

    api = TwitterClient()
    tweets = api.get_tweets(query=query, count=count)

    ptweets = [tweet for tweet in tweets if tweet['sentiment'] == 'positive']
    ntweets = [tweet for tweet in tweets if tweet['sentiment'] == 'negative']
    neutral_tweets = [tweet for tweet in tweets if tweet['sentiment'] == 'neutral']

    positive_percent = round(100 * len(ptweets) / len(tweets), 2)
    negative_percent = round(100 * len(ntweets) / len(tweets), 2)
    neutral_percent = round(100 * len(neutral_tweets) / len(tweets), 2)

    response = {
        'positive_percent': positive_percent,
        'negative_percent': negative_percent,
        'neutral_percent': neutral_percent,
        'positive_tweets': [{'text': tweet['text'], 'url': tweet['tweet_url']} for tweet in ptweets[:10]],
        'negative_tweets': [{'text': tweet['text'], 'url': tweet['tweet_url']} for tweet in ntweets[:10]],
        'neutral_tweets': [{'text': tweet['text'], 'url': tweet['tweet_url']} for tweet in neutral_tweets[:10]]
    }
    return jsonify(response)
