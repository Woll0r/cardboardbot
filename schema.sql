CREATE TABLE cardboardactions(id INTEGER PRIMARY KEY, action TEXT, type TEXT);
CREATE TABLE cardboardlinks(id INTEGER PRIMARY KEY, timestamp INTEGER, name TEXT, url TEXT, title TEXT, domain TEXT);
CREATE TABLE cardboardlog(id INTEGER PRIMARY KEY, timestamp INTEGER, name TEXT, message TEXT);
CREATE TABLE cardboardnick(id INTEGER PRIMARY KEY, jid TEXT, nick TEXT, timestamp INTEGER DEFAULT 0);
CREATE INDEX cardboardlinks_timestamp_ix ON cardboardlinks(timestamp);
CREATE INDEX cardboardlog_timestamp_ix ON cardboardlog(timestamp);
CREATE INDEX cardboardnick_jid_ix ON cardboardnick(jid);
CREATE INDEX cardboardnick_nick_ix ON cardboardnick(nick);
CREATE INDEX cardboardnick_nick_ix_nocase ON cardboardnick(nick COLLATE NOCASE);
