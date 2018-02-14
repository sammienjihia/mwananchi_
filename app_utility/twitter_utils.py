
import time
import tweepy
from Mwananchi import settings
from HTMLParser import HTMLParser
from nltk.corpus import stopwords
import string
from collections import Counter

from pattern.en import sentiment
from twitter.models import TwitterMentions, TwitterTimeline, TwitterResult


def search_twitter(key_word, aspirant):
    try:
        searchQuery = key_word # this is what we're searching for
        maxTweets = 1000  # Some arbitrary large number
        tweetsPerQry = 100  # this is the max the API permits

        consumer_key = settings.TWITTER_TOKEN
        consumer_secret = settings.TWITTER_SECRET
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        max_id = -1L
        tweetCount = 0
        api = tweepy.API(auth)
        sinceId = None

        tweets_data = []
        count_all = Counter()

        while tweetCount < maxTweets:
            try:
                if max_id <= 0:
                    if (not sinceId):
                        new_tweets = api.search(q=searchQuery, count=tweetsPerQry)
                    else:
                        new_tweets = api.search(q=searchQuery, count=tweetsPerQry,
                                                since_id=sinceId)
                else:
                    if (not sinceId):
                        new_tweets = api.search(q=searchQuery, count=tweetsPerQry,
                                                max_id=str(max_id - 1))
                    else:
                        new_tweets = api.search(q=searchQuery, count=tweetsPerQry,
                                                max_id=str(max_id - 1),
                                                since_id=sinceId)
                if not new_tweets:
                    break

                try:
                    TwitterResult.objects.filter(aspirant=aspirant).delete()
                except:
                    pass

                for tweet in new_tweets:
                    polarity_subjectivity = sentiment(tweet.text)
                    polarity = polarity_subjectivity[0]
                    tweet_sentiment = 'NEUTRAL'
                    if polarity_subjectivity[1] > 0:
                        if polarity_subjectivity[0] >= 0.1:
                            tweet_sentiment = 'POSITIVE'
                        else:
                            tweet_sentiment = 'NEGATIVE'

                    unescape = HTMLParser().unescape
                    location = tweet.user.location.lower()

                    if "nairobi" in location:
                        location = "Nairobi"
                    elif location == "" or location == None:
                        location = "Unspecified"
                    else:
                        location = "Other"

                    author = tweet.user.screen_name
                    tweet_id = str(tweet.id)
                    twitter_url = "https://twitter.com/"
                    tweet_url = twitter_url + author + "/" + "status" + "/" + tweet_id


                    tweets_data.append(
                    {
                            'tweetid': tweet.id,
                            'text': unescape(tweet.text),
                            'author': tweet.user.screen_name,
                            'date': tweet.created_at,
                            'followers': tweet.user.followers_count,
                            'retweet': tweet.retweet_count,
                            'favourite': tweet.user.favourites_count,
                            'tweet_sentiment':tweet_sentiment,
                            'polarity': polarity,
                            'tweet_url': tweet_url
                    })

                    twitter_result = TwitterResult(
                        aspirant=aspirant,
                        key_word=key_word,
                        tweet_id=tweet.id,
                        text=tweet.text.encode('ascii', 'ignore').decode('ascii'),
                        author=tweet.user.screen_name,
                        date=tweet.created_at,
                        followers=tweet.user.followers_count,
                        retweet=tweet.retweet_count,
                        tweet_sentiment=tweet_sentiment,
                        polarity=polarity,
                        place=location
                    )
                    twitter_result.save()

                    tweetCount += len(new_tweets)
                    max_id = new_tweets[-1].id
                    punctuation = list(string.punctuation)
                    stop = stopwords.words('english') + punctuation + ['rt', 'via']

                    terms_only = [term for term in tweet.text.lower().split() if
                                  term not in stop and not term.startswith(('#', '@'))]
                    count_all.update(terms_only)
                    count_all.most_common(100)
                    print count_all.most_common(10)

            except tweepy.TweepError as e:
                # Just exit if any error
                break

    except tweepy.RateLimitError:
        time.sleep(60 * 15)

    return tweets_data


def post_sth_to_twitter(post, aspirant):
    consumer_key = settings.TWITTER_TOKEN
    consumer_secret = settings.TWITTER_SECRET
    try:
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        access_token = aspirant.twitter_oauth_token
        access_token_secret = aspirant.twitter_oauth_secret
        auth.set_access_token(access_token, access_token_secret)
        api = tweepy.API(auth)
        api.configuration()
        try:
            api.update_status(post)
            return True
        except Exception, e:
            print(str(e))
            return False
    except Exception, e:
        print(str(e))
        return False



def twitter_user_timeline(key_word, aspirant):
    try:
        searchQuery = key_word # this is what we're searching for
        maxTweets = 1000  # Some arbitrary large number
        tweetsPerQry = 100  # this is the max the API permits

        consumer_key = settings.TWITTER_TOKEN
        consumer_secret = settings.TWITTER_SECRET
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        max_id = -1L
        tweetCount = 0
        api = tweepy.API(auth)
        sinceId = None

        tweets_data = []
        count_all = Counter()

        while tweetCount < maxTweets:
            try:
                # if max_id <= 0:
                #     if (not sinceId):
                #         new_tweets = api.user_timeline(q=searchQuery, count=tweetsPerQry)
                #     else:
                #         new_tweets = api.user_timeline(q=searchQuery, count=tweetsPerQry,
                #                                 since_id=sinceId)
                # else:
                #     if (not sinceId):
                #         new_tweets = api.user_timeline(q=searchQuery, count=tweetsPerQry,
                #                                 max_id=str(max_id - 1))
                #     else:
                #         new_tweets = api.user_timeline(q=searchQuery, count=tweetsPerQry,
                #                                 max_id=str(max_id - 1),
                #                                 since_id=sinceId)



                for status in tweepy.Cursor(api.user_timeline).items():
                    new_tweets = status

                if not new_tweets:
                    break

                try:
                    TwitterTimeline.objects.filter(aspirant=aspirant).delete()
                except:
                    pass

                for tweet in new_tweets:
                    polarity_subjectivity = sentiment(tweet.text)
                    polarity = polarity_subjectivity[0]
                    tweet_sentiment = 'NEUTRAL'
                    if polarity_subjectivity[1] > 0:
                        if polarity_subjectivity[0] >= 0.1:
                            tweet_sentiment = 'POSITIVE'
                        else:
                            tweet_sentiment = 'NEGATIVE'

                    unescape = HTMLParser().unescape

                    tweets_data.append(
                    {
                            'tweetid': tweet.id,
                            'text': unescape(tweet.text),
                            'author': tweet.user.screen_name,
                            'date': tweet.created_at,
                            'followers': tweet.user.followers_count,
                            'retweet': tweet.retweet_count,
                            'favourite': tweet.favorite_count,
                            'tweet_sentiment':tweet_sentiment,
                            'polarity': polarity
                    })

                    twitter_result = TwitterTimeline(
                        aspirant=aspirant,
                        key_word=key_word,
                        tweet_id=tweet.id,
                        text=tweet.text.encode('ascii', 'ignore').decode('ascii'),
                        author=tweet.user.screen_name,
                        date=tweet.created_at,
                        followers=tweet.user.followers_count,
                        retweet=tweet.retweet_count,
                        tweet_sentiment=tweet_sentiment,
                        polarity=polarity
                    )
                    twitter_result.save()

                    tweetCount += len(new_tweets)
                    max_id = new_tweets[-1].id
                    punctuation = list(string.punctuation)
                    stop = stopwords.words('english') + punctuation + ['rt', 'via']

                    terms_only = [term for term in tweet.text.lower().split() if
                                  term not in stop and not term.startswith(('#', '@'))]
                    count_all.update(terms_only)
                    count_all.most_common(100)
                    print count_all.most_common(10)

            except tweepy.TweepError as e:
                # Just exit if any error
                break

    except tweepy.RateLimitError:
        time.sleep(60 * 15)

    return tweets_data


def twitter_timeline(screen_name, aspirant):
    try:
        consumer_key = settings.TWITTER_TOKEN
        consumer_secret = settings.TWITTER_SECRET
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        api = tweepy.API(auth)
        new_tweets = []
        try:
            TwitterTimeline.objects.filter(aspirant=aspirant).delete()
        except:
            pass

        for status in tweepy.Cursor(api.user_timeline, screen_name=screen_name).items():
            print

            print "\n"
            print sentiment(status.text)
            print status._json
            print "\n"
            polarity_subjectivity = sentiment(status.text)
            polarity = polarity_subjectivity[0]

            tweet_sentiment = 'NEUTRAL'
            if polarity_subjectivity[1] > 0:
                if polarity_subjectivity[0] >= 0.1:
                    tweet_sentiment = 'POSITIVE'
                else:
                    tweet_sentiment = 'NEGATIVE'


            twitter_result = TwitterTimeline(
                aspirant=aspirant,
                status_id=status.id,
                status_text=status.text.encode('ascii', 'ignore').decode('ascii'),
                favourite=status.favorite_count,
                created_at=status.created_at,
                followers=status.user.followers_count,
                retweet_count=status.retweet_count,
                tweet_sentiment=tweet_sentiment,
                polarity=polarity
            )
            twitter_result.save()


    except tweepy.TweepError as e:
        print e
        print ("This is the exception error")



##### tweet url method
#for tweets in new_tweets:
#...     author = tweets.user.screen_name
#...     tweet_id = str(tweets.id)
#...     twitter_url = "https://twitter.com/"
#...     tweet_url = twitter_url + author + "/" + "status" + "/" + tweet_id
#...     print tweets.text
#...     print tweet_url


