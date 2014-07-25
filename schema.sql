CREATE TABLE IF NOT EXISTS cardboardactions(id INTEGER PRIMARY KEY, action TEXT, type TEXT);
CREATE TABLE IF NOT EXISTS cardboardlinks(id INTEGER PRIMARY KEY, timestamp INTEGER, name TEXT, url TEXT, title TEXT, domain TEXT);
CREATE TABLE IF NOT EXISTS cardboardlog(id INTEGER PRIMARY KEY, timestamp INTEGER, name TEXT, message TEXT);
CREATE TABLE IF NOT EXISTS cardboardnick(id INTEGER PRIMARY KEY, jid TEXT, nick TEXT);