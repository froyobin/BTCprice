import requests
import json
import numpy as np
import time
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation


pricelist = []
timelist = []
records = []
fig, ax = plt.subplots()
url = "https://127.0.0.1:4356/range"
itemsnum = 100

time_text = ax.text(0.05, 0.9, '', transform=ax.transAxes)


ln, = plt.plot(timelist, pricelist)

def query_range(url, itemsnum):

    Params = {'range': itemsnum}
    data = json.dumps(Params)
    ret = requests.post(url, json=data,verify=False)

    records = ret.json()


    return records

    # resultlist = json.load(ret.content)
    # print(resultlist)


def showinit():
   
    for each in records:
        pricelist.append(each['price'])
    ln, = plt.plot(timelist, pricelist, 'ro')
    textmsg = "current price {}".format(pricelist[-1])

    time_text.set_text(textmsg)

    return ln,  time_text


def update(frame):

    records = query_range(url, 1)
    pricelist.pop(0)
    pricelist.append(records[-1]['price'])
    # timelist.pop(0)
    # timelist.append(records[-1]['time'])
    ln.set_data(timelist, pricelist)
    textmsg = "current price {}".format(pricelist[-1])
    # ax.text(2, 6, textmsg, fontsize=15)
    time_text.set_text(textmsg)
    return ln, time_text


if __name__ == "__main__":
  
    records = query_range(url, itemsnum)
    timelist = [i for i in range(0, itemsnum)]
    FuncAnimation(fig, update, frames=timelist,
                    init_func=showinit, blit=True, interval=1000)
    plt.show()
