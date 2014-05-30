#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sqlite3
import urlparse

try:
    con = sqlite3.connect('cardboardlog.db', isolation_level=None)
    con.row_factory = sqlite3.Row
    cur = con.cursor()

    cur.execute('SELECT * FROM cardboardlinks;')
    results = cur.fetchall()

    for row in results:
        id = row['id']
        url = row['url']

        hostname = urlparse.urlparse(url).hostname.split(".")
        hostname = ".".join(len(hostname[-2]) < 4 and hostname[-3:] or hostname[-2:])

        print hostname

        cmd = 'UPDATE cardboardlinks SET domain=? WHERE id=?'
        cur.execute(cmd, (hostname, id))

except sqlite3.Error, e:
    print "Error %s:" % e.args[0]
    exit(1)

finally:
    if con:
        con.close()
