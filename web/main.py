import requests
import json
import numpy as np
import time
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import matplotlib.dates as mdates
import datetime
import urllib3
import sys
import certifi

left, width = .05, .5
bottom, height = .25, .5
right = left + width
top = bottom + height
pricelist = []
timelist = []
timelistdate = []
records = []
fig, ax = plt.subplots()
mintarget = 0
maxtarget = 0
url = "https://192.168.1.124:4356/range"
itemsnum = 500

time_text = ax.text(left,bottom, '', transform=ax.transAxes,color='red')


ln, = plt.plot(timelist, pricelist)

def query_range(url, itemsnum):

    Params = {'range': itemsnum}
    data = json.dumps(Params)
    ret = requests.post(url, json=data,verify=False)

    records = ret.json()


    return records

    # resultlist = json.load(ret.content)
    # print(resultlist)

def findmaxmin(price, timelist):
    npprice = np.array(price)
    minval = np.ndarray.min(npprice)
    maxval = np.ndarray.max(npprice)
    minindex = np.where(npprice == np.amin(npprice))
    maxindex = np.where(npprice == np.amax(npprice))

    timemaxdatetime = timelist[maxindex[0][-1]]
    timemindatetime = timelist[minindex[0][-1]]

    timemax =  timemaxdatetime.strftime("%H:%M:%S")
    timemin =  timemindatetime.strftime("%H:%M:%S")

    return [maxval, minval], [timemax, timemin]

def showinit():
    global pricelist
    global timelistdate
    pricelist = []
    timelistdate = []
    for each in records:
        pricelist.append(each['price'])
        try:
            datetime_object = datetime.datetime.strptime(each['time'], '%b-%d %H:%M:%S')
        except ValueError as ve:
            print('ValueError Raised:', ve)
        timelistdate.append(datetime_object)
    priceret, timeret = findmaxmin(pricelist, timelistdate)

    textmsg = "current price {}\n Highest price {} at {}\n Low price {} at {}\n".format(
        pricelist[-1], priceret[0],timeret[0], priceret[1], timeret[1])
    time_text.set_text(textmsg)
   
    # plt.gcf().autofmt_xdate()
    # myFmt = mdates.DateFormatter('%d %H:%M:%S')
    # plt.gca().xaxis.set_major_formatter(myFmt)
    ln, = plt.plot(timelist, pricelist, 'ro')
    return ln,  time_text


def update(frame):

    records = query_range(url, 1)
    pricelist.pop(0)
    pricelist.append(records[-1]['price'])

    timelistdate.pop(0)
    try:
        datetime_object = datetime.datetime.strptime(records[-1]['time'], '%b-%d %H:%M:%S')
    except ValueError as ve:
        print('ValueError Raised:', ve)
    
    timelistdate.append(datetime_object)
    priceret, timeret = findmaxmin(pricelist, timelistdate)
    
    textmsg = "current price {}\n Highest price {} at {}\n Low price {} at {}\n".format(
        pricelist[-1], priceret[0],timeret[0], priceret[1], timeret[1])
   

    ln.set_data(timelist, pricelist)
    time_text.set_text(textmsg)
    if pricelist[-1] > maxtarget:
        msg = "Good news, the price now is {}".format(pricelist[-1])
        post_to_slack(msg)

    if pricelist[-1] < mintarget:
        msg = "Bad news, the price now is {}".format(pricelist[-1])
        post_to_slack(msg)

    return ln, time_text






def post_to_slack(message):
    webhook_url = "https://hooks.slack.com/services/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"
    requests.post(webhook_url, json={'text': message})
    # http = urllib3.ProxyManager(proxy_url=proxy, cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())
    # slack_url = "https://hooks.slack.com/services/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"
    
    # encoded_data = json.dumps({'text': message}).encode('utf-8')
    # response = http.request("POST", slack_url, body=encoded_data, headers={'Content-Type': 'application/json'})
    # print(str(response.status) + str(response.data))


if __name__ == "__main__":
    mintarget = float(sys.argv[1])
    maxtarget = float(sys.argv[2])
    records = query_range(url, itemsnum)
    timelist = [i for i in range(0, len(records))]
    FuncAnimation(fig, update, frames=timelist,
                    init_func=showinit, blit=True, interval=10000)
    plt.show()
