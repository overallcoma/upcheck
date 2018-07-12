import os
import datetime
import sqlite3
import schedule
from sqlite3 import Error
import tweepy
import time

try:
    consumer_key = os.environ['UPCHECK_TWITTER_CONSUMER_KEY']
except Error as e:
    print(e)
    exit(1)
try:
    consumer_secret = os.environ['UPCHECK_TWITTER_CONSUMER_SECRET']
except Error as e:
    print(e)
    exit(1)
try:
    access_token = os.environ['UPCHECK_TWITTER_ACCESS_TOKEN']
except Error as e:
    print(e)
    exit(1)
try:
    access_token_secret = os.environ['UPCHECK_TWITTER_ACCESS_TOKEN_SECRET']
except Error as e:
    print(e)
    exit(1)
try:
    dbfile = os.environ['UPCHECK_DB_LOCATION']
except Error as e:
    print(e)
    exit(1)


def post_to_twitter(tweet_string):
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth)
    api.update_status(tweet_string)


def get_outage_last_24h():
    try:
        connection = sqlite3.connect(dbfile, detect_types=sqlite3.PARSE_DECLTYPES)
        cursor = connection.cursor()
        yesterday = (datetime.datetime.now()) - (datetime.timedelta(days=1))
        cursor.execute("SELECT out_start FROM upcheck")
        total_outages = cursor.fetchall()
        valid_outages = []
        for outage in total_outages:
            if outage[0] >= yesterday:
                valid_outages.append(outage)
        valid_outages = len(total_outages)
        print(valid_outages)
        return valid_outages
    except Error as t:
        print(t)


def tweet_outage_24h():
    outage_count = int(get_outage_last_24h())
    if outage_count.__int__() <= 0:
        tweet_string = "No outages in the last 24 hours!  Keep up the good work @Get_Spectrum @Ask_Spectrum!"
    elif outage_count.__int__() >= 1:
        tweet_string = "There were {0} total outages yesterday @Get_Spectrum @Ask_Spectrum.  Please look into this!  #customerservice #icanhazinternet".format(outage_count)
    post_to_twitter(tweet_string)
    print("24 Hour Report Posted to Twitter")


def outage_report_24h():
    tweet_outage_24h()


schedule.every().day.at("07:30").do(outage_report_24h)

while True:
    schedule.run_pending()
    time.sleep(1)
