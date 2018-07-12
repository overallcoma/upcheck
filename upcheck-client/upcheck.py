import speedtest
import xml.etree.cElementTree as et
import schedule

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

    xml_root = et.Element("SpeedtestResults")
    et.SubElement(xml_root, "download").text = download_speed
    et.SubElement(xml_root, "upload").text = upload_speed
    et.SubElement(xml_root, "ping").text = ping

    xml_output = et.tostring(xml_root)
    xml_output_file = open("output.xml", "wb+")
    xml_output_file.write(xml_output)


#primary_operation()

schedule.every().hour.do(primary_operation())