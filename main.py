#! usr/bin/env python

import requests
import csv
from zipfile import ZipFile
import datetime
import redis
from os.path import join, exists
from os import mkdir


class Downloader:

    def __init__(self, out_dir, redis_db=None):
        self.date = datetime.date.today()
        self.out_dir = out_dir
        if not exists(self.out_dir):
            mkdir(self.out_dir)
        self.fileToBeDownloaded = "EQ" + \
            self.date.strftime('%d%m%y') + "_CSV.ZIP"
        # self.fileToBeDownloaded = "EQ220118_CSV.ZIP"
        self.fileToExtract = self.fileToBeDownloaded.split('_')[0] + ".CSV"
        self.csvFile = join(self.out_dir, self.fileToExtract)
        self.redis_db = redis_db

    def StoreData(self):
        if self.redis_db is not None:
            self.redis_db.flushall()
            with open(self.csvFile) as f:
                reader = csv.DictReader(f)

                for row in reader:
                    d = dict({'code': row['SC_CODE'], 'open': row['OPEN'], 'high': row[
                        'HIGH'], 'low': row['LOW'], 'close': row['CLOSE']})

                    self.redis_db.hmset(row['SC_NAME'].strip(), d)

                self.redis_db.save()
            # print(self.redis_db.get('HDFC'))

    def GetData(self):

        print("Fetching file for {0}....".format(self.date))
        r = requests.get(
            'http://www.bseindia.com/download/BhavCopy/Equity/' + self.fileToBeDownloaded)

        print("Response code:", r.status_code)
        if r.status_code == requests.codes.ok:
            print("Creating zip file: ", self.fileToBeDownloaded)

            with open(join(self.out_dir, self.fileToBeDownloaded), 'wb+') as f:
                f.write(r.content)
                ZipFile(f).extract(self.fileToExtract, self.out_dir)
            return True
        else:
            print("Error in fetching file")
            return False

if __name__ == "__main__":
    d = Downloader(out_dir="data", redis_db=redis.StrictRedis())
    if d.GetData():
        d.StoreData()
        print("Fetched data successfully")
    else:
        print("!! Error in fetching data !!")
