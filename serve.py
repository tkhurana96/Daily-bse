import cherrypy
from datetime import datetime
import redis
import os
from apscheduler.triggers.cron import CronTrigger
from apscheduler.schedulers.background import BackgroundScheduler
from jinja2 import Environment, FileSystemLoader
from main import Downloader

scheduler = BackgroundScheduler()
scheduler.start()
redis_db = redis.StrictRedis().from_url(
    os.environ.get("REDIS_URL"), decode_responses=True)
env = Environment(loader=FileSystemLoader('templates'))


class StockData(object):

    @staticmethod
    @scheduler.scheduled_job(trigger=CronTrigger(year='*', month='*',
                                                 day='*', week='*', hour=23, minute=19, second=0, start_date=datetime.now()))
    def updateDB():
        print("=" * 50 + "\nUpdating\n" + "=" * 50)
        dl = Downloader(out_dir="data", redis_db=redis_db)
        if dl.GetData():
            dl.StoreData()
        else:
            print("Error in updating DB")

    def __init__(self):
        self.updateDB()

    @cherrypy.expose
    def index(self):
        # TODO: Get first 10 entries of redis
        possible_keys = redis_db.keys()
        possible_keys = possible_keys[:10]
        pipeline = redis_db.pipeline()
        pipeline.multi()
        for key in possible_keys:
            pipeline.hgetall(key)
        ans = pipeline.execute()

        tmpl = env.get_template('index.html')
        return tmpl.render(data=dict(zip(possible_keys, ans)))

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def searchResponse(self, name):
        # TODO: Perform validation of user input
        name = name.upper()
        possible_keys = redis_db.keys(pattern='*' + name + '*')

        pipeline = redis_db.pipeline()
        pipeline.multi()
        for key in possible_keys:
            pipeline.hgetall(key)
        ans = pipeline.execute()

        return dict(zip(possible_keys, ans))


cherrypy.quickstart(StockData(), '/')
