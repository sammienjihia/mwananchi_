import json
from django.shortcuts import render
import tweepy
from client.models import Client
import time
from twitter.forms import Twitter_SearchForm
from twitter.models import TwitterMentions, TwitterTimeline
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from datetime import datetime, timedelta
from django.db import connection
from django.db.models import Count
from json_response import JsonResponse
from datetime_truncate import truncate
from django.template import RequestContext, Template

from collections import Counter

from nltk.corpus import stopwords
import string
#import pandas
import re

from pattern.en import sentiment

from app_utility import text_analysis
from app_utility import twitter_utils
from twitter.models import TwitterMentions, TwitterTimeline, TwitterResult

# Create your views here.

consumer_key = settings.TWITTER_TOKEN
consumer_secret = settings.TWITTER_SECRET


@login_required(login_url='accounts:login_page')
def trends(request):
    tokens = Client.objects.get(user=request.user.id)
    access_token = tokens.twitter_oauth_token
    access_token_secret = tokens.twitter_oauth_secret
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth)
    trends1 = api.trends_place(23424863)
    data = trends1[0]
    trends = data['trends']
    names = [trend['name'] for trend in trends]
    trendsName = ' '.join(names)
    return JsonResponse(trendsName, safe=False)


@login_required(login_url='accounts:login_page')
def tweet_search(request):
    count_all = Counter()
    aspirant = Client.objects.get(user=request.user)
    title = "Search Twitter"
    form = Twitter_SearchForm(request.POST or None)
    context = {"title": title}

    if request.method == 'POST':
        twitter_results_template = 'twitter/tweet_results.html'
        try:
            filter_data = request.POST['filter_data']
            sentiment = request.POST['sentiment']
            key_word = request.POST['key_word']
            key_word = key_word.strip()
            twitter_data = TwitterResult.objects.filter(aspirant=Client.objects.get(user=request.user))
            if len(key_word) > 0 and len(sentiment) > 0:
                twitter_data = twitter_data.filter(text__icontains=key_word, tweet_sentiment__icontains=sentiment)
            elif len(key_word) > 0 and len(sentiment) == 0:
                twitter_data = twitter_data.filter(text__icontains=key_word)
            elif len(key_word) == 0 and len(sentiment) > 0:
                twitter_data = twitter_data.filter(tweet_sentiment__icontains=sentiment)
        except:
            keyword = request.POST['searchword']
            twitter_data = twitter_utils.search_twitter(keyword, aspirant)
        context = {"tweets": twitter_data}
        return render(request, twitter_results_template, context)
    else:
        template = 'twitter/tweet_search.html'
        trending = []
        access_token = aspirant.twitter_oauth_token
        access_token_secret = aspirant.twitter_oauth_secret
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)
        api = tweepy.API(auth)
        trends1 = api.trends_place(23424863)
        data = trends1[0]
        trends = data['trends']
        for trend in trends:
            trending.append(trend['name'])
        context = {"form": form, "trends": trending, "title": title}

        return render(request, template, context)


@login_required(login_url='accounts:login_page')
def search_tweet_from_hash_tag(request, hashtag):
    twitter_data = twitter_utils.search_twitter(hashtag, Client.objects.get(user=request.user))
    template = 'twitter/tweet_results.html'
    context = {"tweets": twitter_data}
    return render(request, template, context)


@login_required(login_url='accounts:login_page')
def timeline_tracker(request):
    twitter_utils.twitter_timeline('sammiedilani', Client.objects.get(user=request.user))
    twitter_data = TwitterTimeline.objects.filter(aspirant=Client.objects.get(user=request.user))
    tweets_data = []
    for tweet in twitter_data:
        tweets_data.append(
            {
             'tweetid': tweet.status_id,
             'text': tweet.status_text,
             'author': tweet.in_reply_to_screen_name,
             'date': tweet.created_at,
             'followers': tweet.followers,
             'retweets': tweet.retweet_count,
             'favourite': tweet.favourite,
             'polarity': tweet.polarity
            })

    template = 'twitter/twitter_timeline.html'
    context = {"tweets": tweets_data}
    return render(request, template, context)


@login_required(login_url='accounts:login_page')
def twitter_mentions(request):
    twitter_data = TwitterMentions.objects.filter(aspirant=Client.objects.get(user=request.user))
    tweets_data = []
    for tweet in twitter_data:
        tweets_data.append(
            {
                'tweetid': tweet.status_id,
                'text': tweet.status_text,
                'author': tweet.in_reply_to_screen_name,
                'date': tweet.created_at,
                'followers': tweet.followers,
                'retweets': tweet.retweet_count,
                'favourite': tweet.favourite,
                'polarity': tweet.polarity
            })

    template = 'twitter/tweet_results.html'
    context = {"tweets": tweets_data}
    return render(request, template, context)


@login_required(login_url='accounts:login_page')
def get_num_of_words(request):
    num_of_words = request.POST.get('num_of_words')
    tweets_res = TwitterResult.objects.filter(aspirant=Client.objects.get(user=request.user)).distinct('text')
    frequent_words = text_analysis.word_count([tweet.text for tweet in tweets_res], num_of_words)
    return HttpResponse(json.dumps(frequent_words))


@login_required(login_url='accounts:login_page')
def get_sentiment_analysis(request):
    tweet_res = TwitterResult.objects.values('tweet_sentiment')\
        .annotate(num=Count('tweet_sentiment')).filter(aspirant=Client.objects.get(user=request.user))
    return_data = []
    for obj in tweet_res:
        return_data.append({
            'sentiment': obj['tweet_sentiment'],
            'count': obj['num']
        })
    print(return_data)
    return HttpResponse(json.dumps(return_data))


@login_required(login_url='accounts:login_page')
def get_tweets_by_region_analysis(request):
    tweet_res = TwitterResult.objects.values('place') \
        .annotate(num=Count('place')).filter(aspirant=Client.objects.get(user=request.user))
    print("=====================================")
    print(tweet_res)
    print("=====================================")
    return_data = []
    for obj in tweet_res:
        return_data.append({
            'region': obj['place'],
            'count': obj['num']
        })
    print(return_data)
    return HttpResponse(json.dumps(return_data))


@login_required(login_url='accounts:login_page')
def get_sentiments_by_region_analysis(request):
    tweets_by_region = TwitterResult.objects.filter(aspirant=Client.objects.get(user=request.user)).values('place').annotate(pos='')




