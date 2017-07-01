import redis
import pickle
from collections import namedtuple
import dateutil.relativedelta as relativedelta

DocMonitorInfo = namedtuple('DocMonitorInfo',
                            ['revision', 'last_monitor_time', 'last_update_time'])


class Database:
    def __init__(self):
        self.redis = redis.StrictRedis(host='localhost', port=6379, db=0)

    def doc_info(self, doc_id):
        """
        Return: DocMonitorInfo of this id, or None if not exists
        """
        res = self.redis.get(doc_id)
        if res is not None:
            res = pickle.loads(res)
        return res

    def set(self, doc_id, doc_info):
        self.redis.set(doc_id, pickle.dumps(doc_info))

    def clear(self):
        for k in self.redis.keys():
            self.redis.delete(k)


class ChangeMonitor:
    """
    The monitor will fetch revision info for possiblely out-dated docs, update
    their `last_monitor_time`, and add updated doc to notification-queue.
    """
    def __init__(self, monitor_time, since_n_days):
        """
        Monitor change since n days from monitor_time

        monitor_time: datetime.datetime
        since_n_days: int
        """
        self.monitor_time = monitor_time
        self.since_n_days = since_n_days
        self.outdated_date = monitor_time - relativedelta.relativedelta(day=since_n_days)

    def filter_possibly_outdated_doc_ids(self, db, doc_ids):
        """
        Given a list of ids, return a new list of possibly outdated ids
        """
        new_doc_ids = []

        def _possibly_oudated(doc_id):
            doc_monitor_info = db.get(doc_id)
            if doc_monitor_info is None:
                new_doc_ids.append(doc_id)
            else:
                last_monitor_time = doc_monitor_info.last_monitor_time
                return last_monitor_time < self.outdated_date
        return list(filter(_possibly_oudated, doc_ids))

    def scan(self, dbx):
        pass
