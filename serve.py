import cherrypy
from datetime import datetime
import redis
from apscheduler.triggers.cron import CronTrigger
from apscheduler.schedulers.background import BackgroundScheduler
from main import Downloader

data = {
    'ABB LTD.': dict({'code': 500002, 'open': 1583, 'high': 1607.4, 'low': 1563.8, 'close': 1597.6}),
    'AEGIS LOGIS': dict({'code': 500003, 'open': 286.15, 'high': 288.2, 'low': 283, 'close': 285})
}

scheduler = BackgroundScheduler()
scheduler.start()
redis_db = redis.StrictRedis()


@scheduler.scheduled_job(trigger=CronTrigger(year='*', month='*',
                                             day='*', week='*', hour=23, minute=19, second=0, start_date=datetime.now()))
def updateDB():
    print("*" * 100, "Updating")
    print(redis_db.keys())
    # TODO: Empty the DB here
    dl = Downloader(redis_db=redis_db)
    if dl.GetData():
        dl.StoreData()
    else:
        print("Error in updating DB")


class StockData(object):

    @cherrypy.expose
    def index(self):
        return open('index.html')

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def searchResponse(self, name):
        # TODO: Perform validation of user input
        try:
            # TODO: Get search results from redis_db
            possible_keys = redis_db.keys(pattern=name)
            return str(possible_keys)
            # return str(data[name])
        except KeyError:
            return str(dict({}))

cherrypy.engine.subscribe('start', updateDB)
cherrypy.quickstart(StockData(), '/')
