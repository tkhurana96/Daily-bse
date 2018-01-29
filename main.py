#! usr/bin/env python

import requests
import csv
from zipfile import ZipFile
import datetime
import redis
from os.path import join, exists
import os


class Downloader:

    def __init__(self, out_dir, redis_db=None):
        self.date = datetime.date.today()
        self.out_dir = out_dir
        if not exists(self.out_dir):
            os.mkdir(self.out_dir)
        self.fileToBeDownloaded = "EQ" + \
            self.date.strftime('%d%m%y') + "_CSV.ZIP"
        self.fallBackFileToBeDownloaded = "EQ240118_CSV.ZIP"
        self.fileToExtract = self.fileToBeDownloaded.split('_')[0] + ".CSV"
        self.csvFile = join(self.out_dir, self.fileToExtract)
        self.redis_db = redis_db

    def StoreData(self):
        if self.redis_db is not None:
            try:
                with open(self.csvFile) as f:
                    reader = csv.DictReader(f)

                    pipeline = self.redis_db.pipeline()
                    pipeline.multi()
                    pipeline.flushall()
                    for idx, row in enumerate(reader):
                        name = row['SC_NAME'].strip()
                        if idx < 10:
                            pipeline.zadd('top10', idx, name)

                        d = dict({'code': row['SC_CODE'], 'open': row['OPEN'], 'high': row[
                            'HIGH'], 'low': row['LOW'], 'close': row['CLOSE']})

                        pipeline.hmset(name, d)

                    pipeline.save()
                    pipeline.execute()
            except:
                print("Error occured in storing data")

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
            self.fileToBeDownloaded = self.fallBackFileToBeDownloaded
            self.fileToExtract = self.fileToBeDownloaded.split('_')[0] + ".CSV"
            self.csvFile = join(self.out_dir, self.fileToExtract)

            print(
                "Error in fetching file, using fallback file url for 24th Jan 2018")
            r = requests.get(
                'http://www.bseindia.com/download/BhavCopy/Equity/' + self.fileToBeDownloaded)
            if r.status_code == requests.codes.ok:
                print("Creating zip file: ", self.fileToBeDownloaded)

                with open(join(self.out_dir, self.fileToBeDownloaded), 'wb+') as f:
                    f.write(r.content)
                    ZipFile(f).extract(self.fileToExtract, self.out_dir)
                return True
            else:
                return False

if __name__ == "__main__":
    r = redis.StrictRedis().from_url(
        os.environ.get("REDIS_URL"), decode_responses=True)
    d = Downloader(
        out_dir="data", redis_db=r)
    if d.GetData():
        print("Fetched data successfully")
        d.StoreData()
    else:
        print("!! Error in fetching data !!")
