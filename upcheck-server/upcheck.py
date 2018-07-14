import os
import datetime
import time
import tweepy
import sqlite3
from sqlite3 import Error
import subprocess
import requests

# Load OS Environment Values hopefully passed from Docker
try:
    urltocheck = os.environ['UPCHECK_URLTOCHECK']
except os.error as e:
    print(e)
    exit(1)
try:
    consumer_key = os.environ['UPCHECK_TWITTER_CONSUMER_KEY']
except os.error as e:
    print(e)
    exit(1)
try:
    consumer_secret = os.environ['UPCHECK_TWITTER_CONSUMER_SECRET']
except os.error as e:
    print(e)
    exit(1)
try:
    access_token = os.environ['UPCHECK_TWITTER_ACCESS_TOKEN']
except os.error as e:
    print(e)
    exit(1)
try:
    access_token_secret = os.environ['UPCHECK_TWITTER_ACCESS_TOKEN_SECRET']
except os.error as e:
    print(e)
    exit(1)
try:
    dbfile = os.environ['UPCHECK_DB_LOCATION']
except os.error as e:
    print(e)
    exit(1)
try:
    target_twitter = os.environ['UPCHECK_TARGET_TWITTER_ACCOUNT']
except os.error as e:
    print(e)
    exit(1)
try:
    target_hashtags = os.environ['UPCHECK_HASHTAGS']
except os.error as e:
    print(e)
    exit(1)
try:
    modem_stats_output = os.environ['UPCHECK_MODEM_SCRAPE_URL']
    checkmodem = True
except os.error as e:
    checkmodem = False
    print(e)


# Sqlite Connection Check
def dbconnect(dbfile):
    try:
        connection = sqlite3.connect(dbfile)
        print(sqlite3.version)
        connection.close()
    except Error as t:
        print(t)
        exit(1)


def db_createtable(dbfile):
    try:
        connection = sqlite3.connect(dbfile)
        cursor = connection.cursor()
        sql = 'CREATE TABLE IF NOT EXISTS upcheck (record_number integer PRIMARY KEY AUTOINCREMENT, out_start TIMESTAMP, out_end TIMESTAMP, out_time text)'
        cursor.execute(sql)
    except Error as t:
        print(t)
        exit(1)


def check_if_up(url):
    try:
        check_return = requests.get(url)
        check_return = check_return.status_code
        if check_return == 200:
            return 0
        else:
            currentime = datetime.datetime.now()
            print("{0} -- Outage Detected".format(currentime))
            return 1
    except requests.exceptions.RequestException as e:
        currentime = datetime.datetime.now()
        print("{0} -- Outage Detected".format(currentime))
        return 1


def time_difference(starttime, endtime):
    try:
        time_delta = endtime - starttime
        string_return = str(time_delta.total_seconds())
        string_return = string_return.split(".")
        return string_return[0]
    except Error as t:
        print(t)
        return 0


def write_out_record(dbfile, starttime, endtime, totaltime):
    try:
        connection = sqlite3.connect(dbfile, detect_types=sqlite3.PARSE_DECLTYPES)
        cursor = connection.cursor()
        cursor.execute("INSERT INTO upcheck VALUES (NULL, ?, ?, ?)", (starttime, endtime, totaltime))
        connection.commit()
        connection.close()
        currentime = datetime.datetime.now()
        print("{0} -- Outage is over".format(currentime))
    except Error as t:
        print(t)


def get_last_outage_time(dbfile):
    try:
        connection = sqlite3.connect(dbfile, detect_types=sqlite3.PARSE_DECLTYPES)
        cursor = connection.cursor()
        cursor.execute("SELECT out_time FROM upcheck WHERE record_number = (SELECT MAX(record_number) from upcheck)")
        last_outage_time = cursor.fetchone()[0]
        connection.commit()
        connection.close()
        return last_outage_time
    except Error as t:
        print(t)
        return 0

    
def get_last_outage_start(dbfile):
    try:
        connection = sqlite3.connect(dbfile, detect_types=sqlite3.PARSE_DECLTYPES)
        cursor = connection.cursor()
        cursor.execute("SELECT out_start FROM upcheck WHERE record_number = (SELECT MAX(record_number) from upcheck)")
        last_outage_start = cursor.fetchone()[0]
        connection.commit()
        connection.close()
        return last_outage_start
    except Error as t:
        print(t)
        return 0


def get_last_outage_end(dbfile):
    try:
        connection = sqlite3.connect(dbfile, detect_types=sqlite3.PARSE_DECLTYPES)
        cursor = connection.cursor()
        cursor.execute("SELECT out_end FROM upcheck WHERE record_number = (SELECT MAX(record_number) from upcheck)")
        last_outage_end = cursor.fetchone()[0]
        connection.commit()
        connection.close()
        return last_outage_end
    except Error as t:
        print(t)
        return 0


def format_datetime_monthdaytime(inputtime):
    try:
        return_time = inputtime.strftime("%B %d at %H:%M")
        return return_time
    except Error as t:
        print(t)
        return 0


def format_datetime_time(inputtime):
    try:
        return_time = inputtime.strftime("%H:%M")
        return return_time
    except Error as t:
        print(t)
        return 0


def get_modem_stats_from_outage():
    try:
        modem_stats_text = requests.get(modem_stats_output)
        modem_stats_text = modem_stats_text.content
        outfile = open(modem_web_output, "w+")
        outfile.write(modem_stats_text)
    except:
        return 2


def post_to_twitter(tweet_string):
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth)
    api.update_status(tweet_string)


def post_twitter_outage_over(dbfile):
    try:
        last_outage_start = get_last_outage_start(dbfile)
        last_outage_end = get_last_outage_end(dbfile)
        last_outage_time = get_last_outage_time(dbfile)
        tweetstring1 = "Just had an outage from {0} UTC to {1} UTC for a total of {2} seconds. {3} {4}".format(format_datetime_time(last_outage_start), format_datetime_time(last_outage_end), last_outage_time, target_twitter, target_hashtags)
        tweetstring2 = "{3} Why did I lose internet from {0}UTC to {1}UTC for a total of {2} seconds? {4}".format(format_datetime_monthdaytime(last_outage_start), format_datetime_monthdaytime(last_outage_end), last_outage_time, target_twitter, target_hashtags)
        post_to_twitter(tweetstring1)
        post_to_twitter(tweetstring2)
        if checkmodem:
            if get_modem_stats_from_outage() != 2:
                tweetstring3 = "{0} The stats from this outage are available at {1} until the next outage".format(target_twitter, modem_stats_output)
            post_to_twitter(tweetstring3)
    except Error as t:
        print(t)


def create_nginx_index_page():
    index_page = "/usr/share/nginx/html/index.html"
    index_page_content = """
    <!DOCTYPE html>
    <html>
    <head>
    <title>UpCheck-Server is Active</title>
    </body>
    </html>"""
    create_index_page = open(index_page, "w+")
    create_index_page.write(index_page_content)

# Start nginx
try:
    subprocess.call(["nginx"])
except subprocess.CalledProcessError as e:
    print(e)
    print("Unable to start nginx")


# set some variables
upchecktable = "upcheck"
outage_active = 0
child_process = "./upcheck-schedule-24h.py"

# launch child process for scheduled tasks
create_nginx_index_page()
subprocess.Popen(['python3', child_process])
modem_web_output = "/usr/share/nginx/html/upcheck-modem.txt"

# the monitoring loop
try:
    dbconnect(dbfile)
except Error as e:
    print("Could not connect to database")
    print(e)
    exit(1)
try:
    db_createtable(dbfile)
    print("Upcheck is active")
except Error as e:
    print("Unable to Create Table")
    print(e)
    exit(1)
while True:
    check_status = check_if_up(urltocheck)
    if check_status == 0:
        if outage_active == 1:
            outage_active = 0
            outage_end = datetime.datetime.now()
            try:
                outage_total_time = time_difference(outage_start, outage_end)
                write_out_record(dbfile, outage_start, outage_end, outage_total_time)
                if checkmodem:
                    get_modem_stats_from_outage()
                post_twitter_outage_over(dbfile)
            except Error as e:
                print(e)
    elif check_status == 1:
        if outage_active == 0:
            outage_start = datetime.datetime.now()
        outage_active = 1
    time.sleep(7)
