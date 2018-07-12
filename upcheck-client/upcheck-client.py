import os
import speedtest
import datetime
import schedule
import sqlite3
import time
from sqlite3 import Error
from subprocess import call
from xml.etree import ElementTree
from xml.etree.ElementTree import Element
from xml.etree.ElementTree import SubElement

xml_web_output = "/usr/share/nginx/html/upcheck-speedtest.xml"

try:
    dbfile = os.environ['UPCHECK_DB_LOCATION']
except Error as e:
    print(e)
    exit(1)


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
        sql = 'CREATE TABLE IF NOT EXISTS upcheck (record_number integer PRIMARY KEY AUTOINCREMENT, timestamp TIMESTAMP, download INTEGER, upload INTEGER, ping INTEGER)'
        cursor.execute(sql)
    except Error as t:
        print(t)
        exit(1)

def write_out_record(dbfile, timestamp, download, upload, ping):
    try:
        connection = sqlite3.connect(dbfile, detect_types=sqlite3.PARSE_DECLTYPES)
        cursor = connection.cursor()
        cursor.execute("INSERT INTO upcheck VALUES (NULL, ?, ?, ?, ?)", (timestamp, download, upload, ping))
        connection.commit()
        connection.close()
    except Error as t:
        print(t)


def average(input):
    return sum(input) / len(input)

def get_average_data():
    connection = sqlite3.connect(dbfile, detect_types=sqlite3.PARSE_DECLTYPES)
    cursor = connection.cursor()
    yesterday = (datetime.datetime.now()) - (datetime.timedelta(days=1))
    cursor.execute("SELECT download FROM upcheck WHERE timestamp > ?", (yesterday,))
    results = cursor.fetchall()
    selected_results = []
    for result in results:
        selected_results.append(result[0])
    speedtest_dl_averrage = average(selected_results)
    speedtest_dl_averrage = round(speedtest_dl_averrage)
    cursor.execute("SELECT upload FROM upcheck WHERE timestamp > ?", (yesterday,))
    results = cursor.fetchall()
    selected_results = []
    for result in results:
        selected_results.append(result[0])
    speedtest_ul_average = average(selected_results)
    speedtest_ul_average = round(speedtest_ul_average)
    cursor.execute("SELECT ping FROM upcheck WHERE timestamp > ?", (yesterday,))
    results = cursor.fetchall()
    selected_results = []
    for result in results:
        selected_results.append(result[0])
    speedtest_ping_average = average(selected_results)
    speedtest_ping_average = round(speedtest_ping_average,2)
    average_array = []
    average_array.append(speedtest_dl_averrage)
    average_array.append(speedtest_ul_average)
    average_array.append(speedtest_ping_average)
    return average_array


def run_speedtest():
    stest = speedtest.Speedtest()
    stest.get_servers()
    stest.get_best_server()
    stest.download()
    stest.upload()
    return stest.results


def bits_to_bytes(inputvalue):
    bits = inputvalue
    megabits = bits / 1000000
    megabits = format(megabits, '.2f')
    return megabits


def primary_operation():
    stest_result = run_speedtest()
    download_speed = str(bits_to_bytes(stest_result.download))
    upload_speed = str(bits_to_bytes(stest_result.upload))
    ping = str(stest_result.ping)

    timestamp = datetime.datetime.now()
    write_out_record(dbfile, timestamp, download_speed, upload_speed, ping)

    average_dl = str(get_average_data()[0])
    average_ul = str(get_average_data()[1])
    average_ping = str(get_average_data()[2])

    print(average_dl)
    print(average_ul)
    print(average_ping)

    xml_root = Element('SpeedtestResults')
    SubElement(xml_root, "average_dl").text = average_dl
    SubElement(xml_root, "average_ul").text = average_ul
    SubElement(xml_root, "average_ping").text = average_ping

    print(xml_root)
    xml_output = ElementTree.tostring(xml_root, encoding='unicode')
    xml_output_file = open(xml_web_output, "w+")
    xml_output_file.write(xml_output)


try:
    call(["nginx"])
except Error as e:
    print(e)
    print("Unable to start nginx")

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

primary_operation()

while True:
    schedule.every().hour.do(primary_operation)
    time.sleep(1)
