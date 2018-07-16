import requests
import html5lib
from bs4 import BeautifulSoup
from prettytable import PrettyTable

modem_log_page = "http://192.168.100.1/cgi-bin/status_cgi"
modem_web_output = "/usr/share/nginx/html/upcheck-modem.txt"


def get_modem_log(table_number):
    modem_log_collect = requests.get(modem_log_page)
    soup = BeautifulSoup(modem_log_collect.text, "html5lib")
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
    return pretty_table_out


log1 = str(get_modem_log(1))
log2 = str(get_modem_log(3))
log3 = str(get_modem_log(7))

write_modem_output = open(modem_web_output, "w+")
write_modem_output.write(log1)
write_modem_output.write(log2)
write_modem_output.write(log3)
