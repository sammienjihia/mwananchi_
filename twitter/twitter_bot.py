import tweepy

TWITTER_TOKEN = 'DASDze82n52S1mWqjaABSOFZD'
TWITTER_SECRET = 'VjDDbowV4qEHdn0v5f8IkiWNwzYlozmww11fularNSpF1t4jqD'

consumer_key = TWITTER_TOKEN
consumer_secret = TWITTER_SECRET


def trends(request):
    trending = []
    access_token = None
    access_token_secret = None
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    api = tweepy.API(auth)
    trends1 = api.trends_place(23424863)
    data = trends1[0]
    trends = data['trends']

    for trend in trends:
        trending.append(trend['name'])
        print trend
