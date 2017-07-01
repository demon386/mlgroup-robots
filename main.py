from __future__ import print_function
import sys
import os
import logging
import dropbox


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


if __name__ == "__main__":
    logging.basicConfig(format='%(levelname)s %(filename)s:%(lineno)dL %(asctime)s %(message)s', level=logging.DEBUG)
    access_token = os.getenv('DROPBOX_TOKEN')
    if not access_token:
        msg = "Failed to get access token, please provide it by setting env variable DROPBOX_TOKEN"
        print(msg, file=sys.stderr)
        logging.fatal(msg)
        sys.exit(1)
    dbx = dropbox.Dropbox(access_token)
    doc_ids = paper_docs_list_doc_ids(dbx)
    for doc_id in doc_ids:
        export_res = export_as_markdown(dbx, doc_id)[0]
        print(export_res.title)
        print(export_res.revision)
        print('----')
