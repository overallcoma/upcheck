import os
import datetime
import sqlite3
import schedule
from sqlite3 import Error
import tweepy
import time
import requests
import xml.etree.cElementTree as et

try:
    urltocheck_speedtest = os.environ['UPCHECK_SPEEDTEST_RESULTS']
except Error as e:
    print(e)
    exit(1)
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
try:
    target_twitter = os.environ['UPCHECK_TARGET_TWITTER_ACCOUNT']
except Error as e:
    print(e)
    exit(1)
try:
    target_hashtags = os.environ['UPCHECK_HASHTAGS']
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
        return valid_outages
    except Error as t:
        print(t)


def tweet_outage_24h():
    outage_count = int(get_outage_last_24h())
    currenttime = datetime.datetime.now()
    yesterday = currenttime - (datetime.timedelta(days=1))
    today_output_time = currenttime.strftime("%B %d")
    yesterday_output_time = yesterday.strftime("%B %d")
    if outage_count.__int__() <= 0:
        tweet_string = "No outages from noon {0} to {1}!  24 hours of Internet!  Keep up the good work {2}!".format(yesterday_output_time, today_output_time, target_twitter)
    elif outage_count.__int__() >= 1:
        tweet_string = "There were {0} total outages from noon {1} to {2} {3}.  Please look into this! {4}".format(outage_count, yesterday_output_time,today_output_time, target_twitter, target_hashtags)
    post_to_twitter(tweet_string)
    print("24 Hour Report Posted to Twitter")


def get_speedtest_xml(speedtesturl):
    speedtest_page = requests.get(speedtesturl)
    speedtest_results = et.fromstring(speedtest_page.text)
    speedtest_dl = speedtest_results.find('average_dl').text
    speedtest_ul = speedtest_results.find('average_ul').text
    speedtest_ping = speedtest_results.find('average_ping').text
    return_list = []
    return_list.append(speedtest_dl)
    return_list.append(speedtest_ul)
    return_list.append(speedtest_ping)
    return return_list


def tweet_speed_24h():
    speed_report = get_speedtest_xml(urltocheck_speedtest)
    average_dl = speed_report[0]
    average_ul = speed_report[1]
    average_ping = speed_report[2]
    tweet_string = "Speedtest Averages for the last 24Hours - {0} Download, {1} Upload, {2} ping. {3}".format(average_dl, average_ul, average_ping, target_twitter)
    post_to_twitter(tweet_string)


def outage_report_24h():
    tweet_outage_24h()


def speed_report_24h():
    tweet_speed_24h()


schedule.every().day.at("17:00").do(outage_report_24h)
schedule.every().day.at("17:05").do(speed_report_24h)

while True:
    schedule.run_pending()
    time.sleep(1)
