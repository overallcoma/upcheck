import os
import datetime
import requests
import time
import subprocess

try:
    urltocheck = os.environ['UPCHECK_URLTOCHECK']
except os.error as e:
    print(e)
    exit(1)


def create_nginx_index_page():
    index_page = "/usr/share/nginx/html/index.html"
    index_page_content = """
    <!DOCTYPE html>
    <html>
    <head>
    <title>UpCheck-Client is Active</title>
    </body>
    </html>"""
    create_index_page = open(index_page, "w+")
    create_index_page.write(index_page_content)


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


try:
    subprocess.call(["nginx"])
except subprocess.CalledProcessError as e:
    print(e)
    print("Unable to start nginx")

outage_active = 0
child_process = "./upcheck-client-scheduledtasks.py"


while True:
    check_status = check_if_up(urltocheck)
    if check_status == 0:
        if outage_active == 1:
            outage_active = 0
    elif check_status == 1:
        if outage_active == 0:
            subprocess.Popen(['python3', child_process])
            outage_active = 1
    time.sleep(10)
