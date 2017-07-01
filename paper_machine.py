import redis
import pickle
from collections import namedtuple

DocMonitorInfo = namedtuple('DocMonitorInfo',
                            ['revision', 'last_monitor_time'])


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
    their `last_monitor_time`, and add updated doc to notification-queue

    """

    def __init__(self):
        pass
