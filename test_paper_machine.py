from datetime import datetime
from paper_machine import Database, DocMonitorInfo


def test_db_set():
    db = Database()
    doc_id = 'abcd'
    doc_info = DocMonitorInfo(0, datetime.now(), datetime.now())

    db.set(doc_id, doc_info)
    retr_info = db.doc_info(doc_id)
    assert doc_info == retr_info

    # try update
    doc_info = DocMonitorInfo(1, datetime.now(), datetime.now())
    db.set(doc_id, doc_info)
    retr_info = db.doc_info(doc_id)
    assert doc_info == retr_info


def test_db_clear():
    db = Database()
    doc_id = 'abcd'
    doc_info = DocMonitorInfo(0, datetime.now(), datetime.now())

    db.set(doc_id, doc_info)
    db.clear()
    retr_info = db.doc_info(doc_id)
    assert retr_info is None


def test_monitor():
    db = Database()
    db.clear()
    last_monitor_time = datetime.strptime("2017-01-01", "%Y-%m-%d")
    print(last_monitor_time)
