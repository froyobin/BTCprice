import requests
import sqlite3
import time
import datetime
import threading
import pytz
from flask import Flask
import json
from flask_cors import CORS

SLEEPTIME = 5
ITEMSIZE = 24*60

url_template = "https://otc-api.huobi.br.com/v1/data/trade-market?country=37" \
               "&currency=1&payMethod=0" \
               "&amount=2000&currPage=1&coinId=1&tradeType=buy&blockType" \
               "=general&online=1"


def fetchdata(minimaltrade):
    url = "https://otc-api.huobi.br.com/v1/data/trade-market?country=37" \
          "&currency=1&payMethod=0&amount={}&currPage=1&coinId=1&tradeType" \
          "=buy&blockType=general&online=1".format(minimaltrade)

    response = requests.get(url)
    response.encoding = 'utf-8'
    data = response.json()
    return data


def getprice(data):
    price = data['data'][0]['price']
    return price


def Createemptydboperation(conn):
    c = conn.cursor()

    # Create table
    c.execute('''CREATE TABLE stocks
                 (date real, name text, pricehigh real, pricelow real, 
                 priceavg real)''')

    # Insert a row of data
    # c.execute("INSERT INTO stocks VALUES ('2006-01-05','BUY','RHAT',100,
    # 35.14)")

    # Save (commit) the changes
    conn.commit()

    # We can also close the connection if we are done with it.
    # Just be sure any changes have been committed or they will be lost.
    conn.close()


def InsertDB(conn, name, pricehigh, pricelow=0, priceavg=0):
    c = conn.cursor()

    currenttime = time.time()

    insertstring = "INSERT INTO stocks VALUES ({},\"{}\",{},{},{})".format(
        currenttime, name, pricehigh, pricelow, priceavg)

    # Insert a row of data
    c.execute(insertstring)

    # Save (commit) the changes
    conn.commit()


def Query(conn):
    c = conn.cursor()
    c.execute('select * from stocks ORDER BY "date" DESC')
    resultrecords = c.fetchall()

    if len(resultrecords) > ITEMSIZE:
        willdelete = resultrecords[-1]
        clause = "DELETE FROM stocks WHERE date={}".format(willdelete[0])
        c.execute(clause)

    # tz = pytz.timezone('Australia/Melbourne')
    # dt = datetime.datetime.fromtimestamp(resultrecords[0][0], tz)
    # print(dt)
    # tz = pytz.timezone('Australia/Melbourne')
    # dt = datetime.datetime.fromtimestamp(resultrecords[1][0], tz)
    # print(dt)
    conn.commit()

    return resultrecords[0]


def queryandput(minimaltrade):
    conn = sqlite3.connect("local.db")
    while True:
        data = fetchdata(minimaltrade)
        price = getprice(data)
        InsertDB(conn, "BTC", price)
        time.sleep(SLEEPTIME)
    conn.close()


app = Flask(__name__)
CORS(app)


@app.route('/')
def ReturnPack():
    conn = sqlite3.connect("local.db")
    record = Query(conn)
    conn.close()
    tz = pytz.timezone('Australia/Melbourne')
    dt = datetime.datetime.fromtimestamp(record[0], tz)
    beautidatetime = dt.strftime("%H:%M:%S")
    package = {"time": beautidatetime, "price": record[2]}

    response = app.response_class(
        response=json.dumps(package),
        status=200,
        mimetype='application/json'
    )
    return response


if __name__ == "__main__":
    currenttime = time.time()
    output = datetime.datetime.utcfromtimestamp(currenttime)
    minimaltrade = 2000

    x = threading.Thread(target=queryandput, args=(minimaltrade,))
    x.start()

    app.run(host="0.0.0.0", port=4356)
    x.join()
