import requests
from bs4 import BeautifulSoup
from prettytable import PrettyTable

modem_log_page = "http://192.168.100.1/cgi-bin/status_cgi"


def get_modem_log(table_number):
    modem_log_collect = requests.get(modem_log_page)
    soup = BeautifulSoup(modem_log_collect.text, "html.parser")
    table = soup.find_all('table')[table_number]
    table_body = table.find('tbody')
    rows = table_body.find_all('tr')
    pt_counter = 0
    for row in rows:
        cols = row.find_all('td')
        cols = [ele.text.strip() for ele in cols]
        cols = [ele for ele in cols]
        if pt_counter == 0:
            pretty_table_out = PrettyTable(cols)
        if pt_counter > 0:
            pretty_table_out.add_row(cols)
        pt_counter = pt_counter + 1
    print(pretty_table_out)


get_modem_log(1)
# get_modem_log(3, "out2.csv") # This will work when they add closing tags to the damned Upstream Table
