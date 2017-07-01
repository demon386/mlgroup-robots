from datetime import datetime
from paper_machine import Database, DocInfo


def test_db_set():
    db = Database()
    doc_id = 'abcd'
    doc_info = DocInfo(0, datetime.now())

    db.set(doc_id, doc_info)
    retr_info = db.doc_info(doc_id)
    assert doc_info == retr_info

    # try update
    doc_info = DocInfo(1, datetime.now())
    db.set(doc_id, doc_info)
    retr_info = db.doc_info(doc_id)
    assert doc_info == retr_info


def test_db_clear():
    db = Database()
    doc_id = 'abcd'
    doc_info = DocInfo(0, datetime.now())

    db.set(doc_id, doc_info)
    db.clear()
    retr_info = db.doc_info(doc_id)
    assert retr_info is None
