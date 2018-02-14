from django.conf.urls import url
from . import views

app_name = 'twitter'

urlpatterns = [
    url(r'^trends/$', views.trends, name='trends'),
    url(r'^tweet_search/$', views.tweet_search, name='tweet_search'),
    url(r'^search_tweet_from_hash_tag/(?P<hashtag>.+)/$', views.search_tweet_from_hash_tag, name='search_tweet_from_hash_tag'),
    url(r'^timeline_tracker$', views.timeline_tracker, name='timeline_tracker'),
    url(r'^twitter_mentions$', views.twitter_mentions, name='twitter_mentions'),
    url(r'^get_num_of_words$', views.get_num_of_words, name='get_num_of_words'),
    url(r'^get_sentiment_analysis$', views.get_sentiment_analysis, name='get_sentiment_analysis'),
    url(r'^get_tweets_by_region_analysis$', views.get_tweets_by_region_analysis, name='get_tweets_by_region_analysis')

]





