from __future__ import print_function
import argparse
import smtplib
import sys
import os
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
import dropbox
import smtplib
from datetime import datetime
from paper_machine import Database, ChangeMonitor


def parse_args():
    parser = argparse.ArgumentParser(description='robots scripts')
    parser.add_argument(
        '-e', '--email', help='send email', action="store_true")
    parser.add_argument(
        '-t',
        '--target',
        help='a file containing email targets, one email per line')
    return parser.parse_args()


def send_email(summary, to):
    username = os.getenv('GMAIL_USER')
    password = os.getenv('GMAIL_PASSWORD')
    if username is None or password is None:
        msg = "Please provide both GMAIL_USER and GMAIL_PASSWORD as env variable"
        print(msg, file=sys.stderr)
        logging.fatal(msg)
        sys.exit(1)

    from_ = '%s@gmail.com' % username
    logging.info("sending email with %s" % from_)
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.ehlo()
    logging.info("startting ttls...")
    server.starttls()
    logging.info("gmail logging in...")
    server.login(username, password)
    logging.info("gmail logged in")

    msg = MIMEMultipart('alternative')
    msg.set_charset('utf8')
    msg['FROM'] = from_
    msg['Subject'] = 'Recent Update from MLGroup [%s]' % datetime.now(
    ).strftime("%Y-%m-%d")
    msg['To'] = ', '.join(to)
    attach = MIMEText(summary, 'html', 'UTF-8')
    msg.attach(attach)

    server.sendmail(from_, to, msg.as_string())
    server.quit()
    logging.info("email sent.")


if __name__ == "__main__":
    logging.basicConfig(
        format='%(levelname)s %(filename)s:%(lineno)dL %(asctime)s %(message)s',
        level=logging.DEBUG)
    args = parse_args()
    access_token = os.getenv('DROPBOX_TOKEN')
    if not access_token:
        msg = "Failed to get access token, please provide it by setting env variable DROPBOX_TOKEN"
        print(msg, file=sys.stderr)
        logging.fatal(msg)
        sys.exit(1)
    dbx = dropbox.Dropbox(access_token)
    db = Database()
    monitor = ChangeMonitor(datetime.now(), 1)
    monitor.scan(dbx, db)
    summary = monitor.summary_update(db)
    print(summary)
    if args.email:
        if not args.target:
            msg = 'Please provide an email target file'
            print(msg, file=sys.stderr)
            logging.fatal(msg)
            sys.exit(1)
        to = [i.strip() for i in open(args.target).readlines()]
        send_email(summary, to)
        db.clear_notify_info()
