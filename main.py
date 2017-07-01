from __future__ import print_function
import sys
import os
import logging
import dropbox
from datetime import datetime
from paper_machine import Database, ChangeMonitor


if __name__ == "__main__":
    logging.basicConfig(format='%(levelname)s %(filename)s:%(lineno)dL %(asctime)s %(message)s', level=logging.DEBUG)
    access_token = os.getenv('DROPBOX_TOKEN')
    if not access_token:
        msg = "Failed to get access token, please provide it by setting env variable DROPBOX_TOKEN"
        print(msg, file=sys.stderr)
        logging.fatal(msg)
        sys.exit(1)
    dbx = dropbox.Dropbox(access_token)
    db = Database()
    monitor = ChangeMonitor(datetime.now(), 7)
    monitor.scan(dbx, db)
