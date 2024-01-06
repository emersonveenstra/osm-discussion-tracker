import changeset_importer

with changeset_importer.conn.cursor() as curs:
	curs.execute('update odt_watched_changesets set snooze_until = null where snooze_until < now()')