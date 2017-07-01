from datetime import datetime
from paper_machine import Database, DocMonitorInfo, DocNotifyInfo


def test_db_set_monitor_info():
    db = Database()
    doc_id = 'abcd'
    doc_info = DocMonitorInfo(0, datetime.now(), datetime.now())

    db.set_monitor_info(doc_id, doc_info)
    retr_info = db.doc_monitor_info(doc_id)
    assert doc_info == retr_info

    # try update
    doc_info = DocMonitorInfo(1, datetime.now(), datetime.now())
    db.set_monitor_info(doc_id, doc_info)
    retr_info = db.doc_monitor_info(doc_id)
    assert doc_info == retr_info


def test_db_clear():
    db = Database()
    doc_id = 'abcd'
    doc_info = DocMonitorInfo(0, datetime.now(), datetime.now())

    db.set_monitor_info(doc_id, doc_info)
    db.clear()
    retr_info = db.doc_monitor_info(doc_id)
    assert retr_info is None


def test_notify():
    doc_notify_info = DocNotifyInfo(1, 'test@test', 'hello')
    db = Database()
    db.clear()
    db.add_notify_info(doc_notify_info)

    res = db.get_notify_info()
    assert list(res)[0] == doc_notify_info

    db.clear_notify_info()
    res = db.get_notify_info()
    assert len(res) == 0
