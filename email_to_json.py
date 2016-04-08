import sys
import os
import configparser
import email
import imaplib
import json
import traceback


def open_connection(config, verbose=False):
    hostname = config.get('mailbox', 'hostname')
    if verbose:
        print('Connecting to', hostname, file=sys.stderr)
    connection = imaplib.IMAP4_SSL(hostname)
    username = config.get('account', 'username')
    password = config.get('account', 'password')
    if verbose:
        print('Logging in as', username, file=sys.stderr)
    connection.login(username, password)
    return connection


def main():
    config = configparser.ConfigParser()
    config.read(['config.ini'])
    try:
        connection = open_connection(config, verbose=True)
    except imaplib.IMAP4.error as e:
        print(e.args[0].decode(), file=sys.stderr)
        exit(1)
    try:
        print("Labels/Directories:", file=sys.stderr)
        status, labels = connection.list()
        if status != "OK":
            print(status, file=sys.stderr)
            exit(1)
        for i in labels:
            print("   ", i.decode(), file=sys.stderr)
        label = None
        if "mailbox" in config and "label" in config["mailbox"]:
            label = config.get('mailbox', 'label')
        label = label or input("label: ")
        connection.select(label)
        resp, items = connection.search(None, "ALL")
        items = items[0].split()
        for n, i in enumerate(items):
            try:
                resp, data = connection.fetch(i, "(RFC822)")
                email_body = data[0][1]
                mail = email.message_from_bytes(email_body)
                payload = None
                for i in range(10):
                    if mail.is_multipart():
                        payload = mail.get_payload(0).get_payload()
                    else:
                        payload = mail.get_payload()
                    if isinstance(payload, str):
                        break
                if not isinstance(payload, str):
                    payload = None
                headers = {}
                for key in mail:
                    for s, e in email.header.decode_header(mail[key]):
                        if isinstance(s, bytes):
                            try:
                                if e is None:
                                    s = s.decode(errors="repace")
                                else:
                                    s = s.decode(e, errors="repace")
                            except LookupError:
                                s = s.decode(errors="replace")
                        headers[key] = s
                print(json.dumps({
                    "payload": payload,
                    "headers": headers,
                }))
                print(n, "/", len(items), file=sys.stderr)
            except Exception as e:
                print(traceback.format_exc(), file=sys.stderr)
        print("Done", file=sys.stderr)
    finally:
        connection.logout()


if __name__ == '__main__':
    if len(sys.argv) > 1:
        print("Usage: {}".format(sys.argv[0]), file=sys.stderr)
        exit(2)
    main()
