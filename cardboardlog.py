#!/usr/bin/python
# -*- coding: utf-8 -*-

import sqlite3
import sys

try:
    con = sqlite3.connect('cardboardlog.db', isolation_level=None)
    cur = con.cursor()
    
    cur.execute("DROP TABLE IF EXISTS cardboardlog")
    cur.execute("CREATE TABLE cardboardlog(id INTEGER PRIMARY KEY, timestamp INTEGER, name TEXT, message TEXT);")
    
    content = []
    with open('cardboardbot.log', "r", "utf-8") as f:
         content = f.readlines()
    
    for line in content:
        name = line[0:25].rstrip()
        message = line[26:len(line)]
        cmd = "INSERT INTO cardboardlog(timestamp, name, message) VALUES (0, ?, ?)"
        cur.execute(cmd, (name, message))
    
except sqlite3.Error, e:    
    print "Error %s:" % e.args[0]
    sys.exit(1)
    
finally:
    if con:
        con.close() 