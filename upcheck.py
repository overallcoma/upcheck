import os
import urllib.request
import datetime
import time
import tweepy
import sqlite3
from sqlite3 import Error, Connection, Cursor

# Load Config File Values
try:
    urltocheck = os.environ['UPCHECK_URLTOCHECK']
except Error as e:
    print(e)
try:
    consumer_key = os.environ['UPCHECK_TWITTER_CONSUMER_KEY']
except Error as e:
    print(e)
try:
    consumer_secret = os.environ['UPCHECK_TWITTER_CONSUMER_SECRET']
except Error as e:
    print(e)
try:
    access_token = os.environ['UPCHECK_TWITTER_ACCESS_TOKEN']
except Error as e:
    print(e)
try:
    access_token_secret = os.environ['UPCHECK_TWITTER_ACCESS_TOKEN_SECRET']
except Error as e:
    print(e)
try: upcheckdblocation = os.environ['UPCHECK_DB_LOCATION']
except Error as e:
    print(e)

upchecktable = "upcheck"
outage_active = 0


# Sqlite Connection Check
def dbconnect(dbfile):
    try:
        connection = sqlite3.connect(dbfile)
        print(sqlite3.version)
    except Error as e:
        print(e)
    finally:
        connection.close()


def db_createtable(dbfile, tablename):
    connection = sqlite3.connect(dbfile)
    cursor = connection.cursor()
    sql = 'CREATE TABLE IF NOT EXISTS upcheck (record_number integer PRIMARY KEY AUTOINCREMENT, out_start DATE, out_end DATE, out_time text)'
    cursor.execute(sql)


try:
    dbconnect(upcheckdblocation)
except:
    print("Could not connect to database")
try:
    db_createtable(upcheckdblocation, upchecktable)
except:
    print("Unable to Create Table")


def check_if_up (url):
    try:
        checkreturn = (urllib.request.urlopen(url).getcode())
        if checkreturn == 200:
            return 0
        else:
            return 1
    except (urllib.error.HTTPError, urllib.error.URLError):
        print("Outage detected")
        return 1
    except Error as e:
        print("Outage Detected")
        print(e)
        return 1


def time_difference(starttime, endtime):
    try:
        time_delta = endtime - starttime
        string_return = str(time_delta.total_seconds())
        string_return = string_return.split(".")
        return string_return[0]
    except Error as e:
        print(e)
        return 0


def write_out_record(dbfile, starttime, endtime, totaltime):
    try:
        connection = sqlite3.connect(dbfile)
        cursor = connection.cursor()
        cursor.execute("INSERT INTO upcheck VALUES (NULL, ?, ?, ?)", (starttime, endtime, totaltime))
        connection.commit()
        connection.close()
        print("Outage is over")
    except Error as e:
        print(e)


def get_last_outage_time(dbfile):
    try:
        connection = sqlite3.connect(dbfile)
        cursor = connection.cursor()
        cursor.execute("SELECT out_time FROM upcheck WHERE record_number = (SELECT MAX(record_number) from upcheck)")
        last_outage_time = cursor.fetchone()[0]
        connection.commit()
        connection.close()
        return last_outage_time
    except Error as e:
        print(e)
        return 0
    
def get_last_outage_start(dbfile):
    try:
        connection = sqlite3.connect(dbfile)
        cursor = connection.cursor()
        cursor.execute("SELECT out_start FROM upcheck WHERE record_number = (SELECT MAX(record_number) from upcheck)")
        last_outage_start = cursor.fetchone()[0]
        connection.commit()
        connection.close()
        return last_outage_start
    except Error as e:
        print(e)
        return 0

def get_last_outage_end(dbfile):
    try:
        connection = sqlite3.connect(dbfile)
        cursor = connection.cursor()
        cursor.execute("SELECT out_end FROM upcheck WHERE record_number = (SELECT MAX(record_number) from upcheck)")
        last_outage_end = cursor.fetchone()[0]
        connection.commit()
        connection.close()
        return last_outage_end
    except Error as e:
        print(e)
        return 0

def format_datetime_monthdaytime(inputtime):
    try:
        return_time = datetime.datetime.strptime(inputtime, '%Y-%m-%d %H:%M:%S.%f')
        return_time = return_time.strftime("%B %d at %H:%M")
        return return_time
    except Error as e:
        print(e)
        return 0


def format_datetime_time(inputtime):
    try:
        return_time = datetime.datetime.strptime(inputtime, '%Y-%m-%d %H:%M:%S.%f')
        return_time = return_time.strftime("%H:%M")
        return return_time
    except Error as e:
        print(e)
        return 0

def post_twitter_outage_over(consumer_key, consumer_secret, access_token, access_token_secret, dbfile):
    try:
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)
        api = tweepy.API(auth)
        last_outage_start = get_last_outage_start(dbfile)
        last_outage_end = get_last_outage_end(dbfile)
        last_outage_time = get_last_outage_time(dbfile)
        tweetstring = "Just had an outage from {0} UTC to {1} UTC for a total of {2} seconds. @GetSpectrum @Ask_Spectrum #customerservice #icanhazinternet".format(format_datetime_time(last_outage_start), format_datetime_time(last_outage_end), last_outage_time)
        api.update_status(tweetstring)
        tweetstring2 = "@GetSpectrum @Ask_Spectrum Why did I lose internet from {0}UTC to {1}UTC for a total of {2} seconds? #Spectrum #customerservice #icanhazinternet".format(format_datetime_monthdaytime(last_outage_start), format_datetime_monthdaytime(last_outage_end), last_outage_time)
        api.update_status(tweetstring2)
    except Error as e:
        print(e)


#the actual operations
while True:
    check_status = check_if_up(urltocheck)
    if check_status == 0:
        if outage_active == 1:
            outage_active = 0
            outage_end = datetime.datetime.now()
            outage_total_time = time_difference(outage_start, outage_end)
            write_out_record(upcheckdblocation, outage_start, outage_end, outage_total_time)
            post_twitter_outage_over(consumer_key, consumer_secret, access_token, access_token_secret, upcheckdblocation)
        time.sleep(10)
    elif check_status == 1:
        if outage_active == 0:
            outage_start = datetime.datetime.now()
        outage_active = 1
        time.sleep(10)
