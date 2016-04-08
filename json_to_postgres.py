import sys
import time
import json
import traceback
import configparser
import postgresql


def write(db, n, m, query):
    headers = m["headers"]
    payload = m["payload"]
    query(n, json.dumps(headers), payload)


def main():
    config = configparser.ConfigParser()
    config.read(['config.ini'])
    hostname = config.get('postgres', 'hostname')
    database = config.get('postgres', 'database')
    db = postgresql.open('pq://{}/{}'.format(hostname, database))
    table = "emails_" + time.strftime("%Y%m%d%H%M%S")
    q = db.execute(
        "CREATE TABLE " + table + " " +
        "(id integer, headers json, payload text)")
    n = 0
    q = db.prepare("INSERT INTO " + table + " VALUES ($1, $2, $3)")
    while True:
        try:
            write(db, n, m=json.loads(input()), query=q)
        except EOFError:
            break
        except Exception as e:
            print(traceback.format_exc(), file=sys.stderr)
        n += 1
        print(n, file=sys.stderr)


if __name__ == '__main__':
    if len(sys.argv) > 1:
        print("Usage: {}".format(sys.argv[0]), file=sys.stderr)
        exit(2)
    main()
