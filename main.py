#! usr/bin/env python

import requests
import csv
from zipfile import ZipFile
import datetime
import redis
from os.path import join


class Downloader:

    def __init__(self, out_dir, redis_db=None):
        self.todays_date = datetime.date.today()
        self.out_dir = out_dir
        # self.fileToBeDownloaded = "EQ" + \
        #     self.todays_date.strftime('%d%m%y') + "_CSV.ZIP"
        self.fileToBeDownloaded = "EQ220118_CSV.ZIP"
        self.fileToExtract = self.fileToBeDownloaded.split('_')[0] + ".CSV"
        self.csvFile = join(self.out_dir, self.fileToExtract)
        self.redis_db = redis_db

    def StoreData(self):
        if self.redis_db is not None:
            with open(self.csvFile) as f:
                reader = csv.DictReader(f)

                for row in reader:
                    d = dict({'code': row['SC_CODE'], 'open': row['OPEN'], 'high': row[
                        'HIGH'], 'low': row['LOW'], 'close': row['CLOSE']})
                    self.redis_db.set(row['SC_NAME'].strip(), d)

            print(self.redis_db.get('HDFC'))

    def GetData(self):

        print("Fetching file for {0}....".format(self.todays_date))
        r = requests.get(
            'http://www.bseindia.com/download/BhavCopy/Equity/' + self.fileToBeDownloaded)

        print("Response code:", r.status_code)
        if r.status_code == requests.codes.ok:
            print("Creating zip file: ", self.fileToBeDownloaded)

            with open(join(self.out_dir, self.fileToBeDownloaded), 'wb+') as f:
                f.write(r.content)
                ZipFile(f).extract(self.fileToExtract, self.out_dir)
            return True
            # if zipfile.is_zipfile(self.fileToBeDownloaded):
            #     print("Extracting file:", self.fileToBeDownloaded)

            #     with zipfile.ZipFile(self.fileToBeDownloaded, mode='r') as myzip:
            #         info = myzip.infolist()
            #         for each in info:
            #             print(type(each), each)
            #         print(dir(info))
            # else:
            #     print("Invalid zip file")
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
