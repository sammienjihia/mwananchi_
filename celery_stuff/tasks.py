import tweepy
import time
from datetime import timedelta
from twitter.models import TwitterTimeline, TwitterMentions
from client.models import Client
from celery.utils.log import get_task_logger
from django.conf import settings
from django.contrib.auth.models import User
from time import sleep
from app_utility.sms_utils import SMS
from app_utility.email_utils import SendEmail
from Mwananchi.celery import app





logger = get_task_logger(__name__)

@app.task(
    name="task_send_email"
)
def task_send_email(recipient, request):
    email = SendEmail()
    print ("jjjjjjjjjjjjjjjjjjjj")
    send_mail = email.send_email(recipient, request)

    logger.info("Email has been sent")
    return send_mail


@app.task(
    name="task_initial_twitter_timeline"
)
def task_initial_twitter_timeline(user):
    auth = tweepy.OAuthHandler(settings.TWITTER_TOKEN, settings.TWITTER_SECRET)
    new_user = Client.objects.get(user=User.objects.get(id=user))
    auth.set_access_token(new_user.twitter_oauth_token, new_user.twitter_oauth_secret)

    api = tweepy.API(auth)
    try:
        searchQuery = new_user.twitter_screen_name
        maxTweets = 1000
        tweetsPerQry = 100

        # If results from a specific ID onwards are reqd, set since_id to that ID.
        # else default to no lower limit, go as far back as API allows
        sinceId = None

        # If results only below a specific ID are, set max_id to that ID.
        # else default to no upper limit, start from the most recent tweet matching the search query.
        max_id = -1L

        tweetCount = 0
        while tweetCount < maxTweets:
            try:
                if (max_id <= 0):
                    if (not sinceId):
                        timeline = api.user_timeline(screen_name=searchQuery, count=tweetsPerQry)
                    else:
                        timeline = api.user_timeline(screen_name=searchQuery, count=tweetsPerQry,
                                                since_id=sinceId)
                else:
                    if (not sinceId):
                        timeline = api.user_timeline(screen_name=searchQuery, count=tweetsPerQry,
                                                max_id=str(max_id - 1))
                    else:
                        timeline = api.user_timeline(screen_name=searchQuery, count=tweetsPerQry,
                                                max_id=str(max_id - 1),
                                                since_id=sinceId)
                if not timeline:
                    break

                for tweet in timeline:
                    timeline_tweets =  TwitterTimeline(status_id=tweet.id,
                                                       status_text=tweet.text,
                                                       retweet_count=tweet.retweet_count,
                                                       in_reply_to_status_id='',
                                                       in_reply_to_status_text='',
                                                       in_reply_to_screen_name='',
                                                       created_at=tweet.created_at,
                                                       aspirant=new_user)
                    timeline_tweets.save()

                tweetCount += len(timeline)
                max_id = timeline[-1].id
            except tweepy.TweepError as e:

                break

    except tweepy.RateLimitError:
        time.sleep(60 * 15)

    logger.info("Finished loading your timeline")


@app.task(
    name="task_twitter_mentions"
)
def task_twitter_mentions():
    auth = tweepy.OAuthHandler(settings.TWITTER_TOKEN, settings.TWITTER_SECRET)
    while True:
        aspirants = Client.objects.all()
        for aspirant in aspirants:
            if aspirant.twitter_oauth_token and aspirant.twitter_oauth_secret:
                auth.set_access_token(aspirant.twitter_oauth_token, aspirant.twitter_oauth_secret)
                try:
                    tweet = TwitterMentions.objects.filter(aspirant_id=aspirant.id).order_by('-created_at')[0]
                    print tweet.created_at
                    status_id = tweet.status_id
                    print status_id
                except:
                    status_id = None
                    print status_id



                api = tweepy.API(auth)
                try:
                    #'@' + client.twitter_screen_name
                    searchQuery = '@Uhuru'
                    maxTweets = 10
                    tweetsPerQry = 5

                    # If results from a specific ID onwards are reqd, set since_id to that ID.
                    # else default to no lower limit, go as far back as API allows
                    sinceId = status_id

                    # If results only below a specific ID are, set max_id to that ID.
                    # else default to no upper limit, start from the most recent tweet matching the search query.
                    max_id = -1L

                    tweetCount = 0
                    while tweetCount < maxTweets:

                        try:
                            if (max_id <= 0):
                                if (not sinceId):
                                    timeline = api.user_timeline(screen_name=searchQuery, count=tweetsPerQry)
                                else:
                                    timeline = api.user_timeline(screen_name=searchQuery, count=tweetsPerQry,
                                                            since_id=sinceId)
                            else:
                                if (not sinceId):
                                    timeline = api.user_timeline(screen_name=searchQuery, count=tweetsPerQry,
                                                            max_id=str(max_id - 1))
                                else:
                                    timeline = api.user_timeline(screen_name=searchQuery, count=tweetsPerQry,
                                                            max_id=str(max_id - 1),
                                                            since_id=sinceId)
                            if not timeline:
                                break

                            for tweet in timeline:

                                timeline_tweets = TwitterMentions(status_id=tweet.id,
                                                                  status_text=tweet.text,
                                                                  retweet_count=tweet.retweet_count,
                                                                  in_reply_to_status_id='',
                                                                  in_reply_to_status_text='',
                                                                  in_reply_to_screen_name='',
                                                                  created_at=tweet.created_at,
                                                                  aspirant=aspirant)
                                timeline_tweets.save()

                            tweetCount += len(timeline)
                            max_id = timeline[-1].id
                        except tweepy.TweepError as e:

                            break

                except tweepy.RateLimitError:
                    time.sleep(60 * 15)

                logger.info("Finished loading your timeline")
                seconds = 60
                sleep(seconds)

            else:
                pass


@app.task(
    name="task_send_batch_sms_from_recipient_list"
)
def task_send_batch_sms_from_recipient_list(recipient_arr, message, user):
    sms = SMS()
    sms.send_batch_sms_from_recipient_list(recipient_arr, message, user)
    logger.info("Finished sending batch sms from recipient list")


@app.task(
    name="task_send_batch_sms_from_excel_upload"
)
def task_send_batch_sms_from_excel_upload(file_name, message, user):
    sms = SMS()
    sms.send_batch_sms_from_excel_upload(file_name, message, user)
    logger.info("Finished sending batch sms from excel upload")


@app.task(
    name="task_send_batch_sms_to_all_subscribers"
)
def task_send_batch_sms_to_all_subscribers(user_id, phone_numbers, message):
    sms = SMS()
    sms.send_batch_sms_to_all_subscribers(user_id, phone_numbers, message)
    logger.info("Finished sending batch sms to all subscriber")

@app.task(
    name="task_send_manifesto_to_subscribers"
)
def task_send_manifesto_to_subscribers(manifesto, aspirant):
    sms = SMS()
    sms.send_manifesto_to_subscribers(manifesto, aspirant)
    logger.info("Finished sending batch campaign to all subscribers")