import changeset_importer

def doBackfill(number_to_backfill):
	with changeset_importer.conn.cursor() as curs:
		curs.execute('select min_state from odt_state')
		min_state = curs.fetchone()["min_state"]
		new_min_state = min_state - number_to_backfill
		print(f'backfilling state files {min_state-1} to {new_min_state}')
		changeset_importer.doReplication(min_state-1, new_min_state-1, -1)
		curs.execute('update odt_state set min_state = %s', (new_min_state,))
		changeset_importer.conn.commit()	

for i in range(500):
	doBackfill(10)