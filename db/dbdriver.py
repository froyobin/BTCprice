import datetime
import pymongo
import hashlib
from coin import coin


class UserDB:
    def __init__(self, address, port, dbname, username, password):
        self.address = address
        self.port = port
        self.connection = pymongo.MongoClient(host=self.address,
                                              port=int(self.port))

        self.db = self.connection[dbname]
        self.UserCollection = self.db["Users"]
        self.db.authenticate(username, password)

    def queryuser(self, sn):
        return self.UserCollection.find_one({"sn": sn})



if __name__ == "__main__":
    address = "localhost:27017"
    port = "27017"
    dbname = "test"
    username = "myTester"
    password = "xyz123"

    h = hashlib.new('ripemd160')
    h.update(password.encode('utf-8'))
    hashpass = h.hexdigest()

    mydb = UserDB(address, port, dbname, username, password)
    startdate = datetime.datetime(2019,1,1,1)
    enddate = datetime.datetime(2019, 12, 12, 12)
    testuser = coin.Coin("user1", hashpass, startdate, enddate, "hello world")
    mydb.UserCollection.insert_one(testuser.__dict__)
