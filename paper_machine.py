import redis
import logging
import dropbox
import pickle
from collections import namedtuple
from datetime import datetime
import dateutil.relativedelta as relativedelta

DocMonitorInfo = namedtuple(
    'DocMonitorInfo', ['revision', 'last_monitor_time', 'last_update_time'])
DocNotifyInfo = namedtuple('DocNotifyInfo', ['doc_id', 'owner', 'title'])


class Database:
    def __init__(self):
        self.redis = redis.StrictRedis(host='localhost', port=6379, db=0)

    def doc_monitor_info(self, doc_id):
        """
        Return: DocMonitorInfo of this id, or None if not exists
        """
        res = self.redis.get(doc_id)
        if res is not None:
            res = pickle.loads(res)
        return res

    def set_monitor_info(self, doc_id, doc_info):
        self.redis.set(doc_id, pickle.dumps(doc_info))

    def clear(self):
        for k in self.redis.keys():
            self.redis.delete(k)

    def add_notify_info(self, info):
        self.redis.sadd('notify', pickle.dumps(info))

    def get_notify_info(self):
        return set(map(pickle.loads, self.redis.smembers('notify')))

    def clear_notify_info(self):
        self.redis.delete('notify')


def paper_docs_list_doc_ids(dbx):
    response = dbx.paper_docs_list(sort_by=dropbox.paper.ListPaperDocsSortBy(
        'created', None))
    doc_ids = response.doc_ids
    while response.has_more:
        doc_ids += dbx.paper_docs_list_continue(response)
    return doc_ids


def export_as_markdown(dbx, doc_id):
    return dbx.paper_docs_download(doc_id,
                                   dropbox.paper.ExportFormat('markdown'))


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
        self.outdated_time = monitor_time - relativedelta.relativedelta(
            days=since_n_days)
        logging.info("outdated_time: %s" % self.outdated_time)

    def filter_possibly_outdated_doc_ids(self, db, doc_ids):
        """
        Given a list of ids, return a new list of possibly outdated ids
        """
        new_doc_ids = []

        def _possibly_oudated(doc_id):
            doc_monitor_info = db.doc_monitor_info(doc_id)
            if doc_monitor_info is None:
                return True
            else:
                last_monitor_time = doc_monitor_info.last_monitor_time
                return last_monitor_time < self.outdated_time

        return list(filter(_possibly_oudated, doc_ids))

    def scan(self, dbx, db):
        logging.info("start scanning...")
        doc_ids = paper_docs_list_doc_ids(dbx)
        logging.info("len(doc_ids) before filtering: %d" % len(doc_ids))
        doc_ids = self.filter_possibly_outdated_doc_ids(db, doc_ids)
        logging.info("len(doc_ids) after filtering: %d" % len(doc_ids))
        for doc_id in doc_ids:
            export_res = export_as_markdown(dbx, doc_id)[0]
            self.update_doc_monitor_info(db, doc_id, export_res)
            self.maybe_add_to_notify_queue(db, doc_id, export_res)

    def update_doc_monitor_info(self, db, doc_id, export_res):
        now = datetime.now()
        doc_monitor_info = db.doc_monitor_info(doc_id)
        new_revision = export_res.revision
        if doc_monitor_info is None:
            logging.info("inserting new doc_id: %s, revision: %d" %
                         (doc_id, new_revision))
            db.set_monitor_info(doc_id,
                                DocMonitorInfo(export_res.revision, now, now))
        else:
            logging.info("updating existing doc_id: %s" % doc_id)
            old_revision = doc_monitor_info.revision
            if new_revision > old_revision:
                update_time = now
                logging.info("revision updated, old: %d, new: %d" % (
                    old_revision, new_revision))
            else:
                update_time = doc_monitor_info.last_update_time
                logging.info(
                    "revision remained the same, maintain last_update_time: %s"
                    % update_time)
            db.set_monitor_info(doc_id,
                                DocMonitorInfo(new_revision, now, update_time))

    def maybe_add_to_notify_queue(self, db, doc_id, export_res):
        """
        If last_update_time > self.oudated_date, add to notify queue
        """
        doc_monitor_info = db.doc_monitor_info(doc_id)
        if doc_monitor_info.last_update_time > self.outdated_time:
            logging.info(
                "add to notify queue. doc_id: %s, last_update_time: %s" %
                (doc_id, doc_monitor_info.last_update_time))
            db.add_notify_info(
                DocNotifyInfo(doc_id, export_res.owner, export_res.title))

    def summary_update(self, db):
        notify_info = db.get_notify_info()
        output = []
        output.append("Recent update from MLGroup Dropbox Paper")
        for info in notify_info:
            last_update_time = db.doc_monitor_info(
                info.doc_id).last_update_time
            output.append("Detected update date: %s<br \>Owner: %s, Doc: %s<br/>" %
                          (last_update_time.strftime('%Y-%m-%d'), info.owner,
                           info.title))
        return '<br />\n'.join(output)
