CREATE TABLE cardboardactions(id INTEGER PRIMARY KEY, action TEXT, type TEXT);
CREATE TABLE cardboardlinks(id INTEGER PRIMARY KEY, timestamp INTEGER, name TEXT, url TEXT, title TEXT);
CREATE TABLE cardboardlog(id INTEGER PRIMARY KEY, timestamp INTEGER, name TEXT, message TEXT);
CREATE TABLE cardboardnick(id INTEGER PRIMARY KEY, jid TEXT, nick TEXT);
