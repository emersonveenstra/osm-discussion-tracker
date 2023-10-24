import gzip
from io import BytesIO
import re
from lxml import etree
from hashlib import sha1
import os
import psycopg
import argparse
import urllib.request
from psycopg.rows import dict_row

conn = psycopg.connect(f"postgresql://{os.environ.get('DB_USER')}:{os.environ.get('DB_PASS')}@{os.environ.get('DB_HOST')}:{os.environ.get('DB_PORT')}/{os.environ.get('DB_NAME')}", row_factory=dict_row)

def parseFile(changesetFile, doReplication):
	parsedCount = 0
	context = etree.iterparse(changesetFile)
	next(context)
	for action, elem in context:
		if(elem.tag != 'changeset'):
			continue

		if (elem.attrib.get('closed_at', False) == False):
			continue

		parsedCount += 1

		csid = elem.attrib['id']
		uid = elem.attrib.get('uid', '0')
		username = elem.attrib.get('user', 'unknown')
		ts = elem.attrib.get('closed_at')

		if(doReplication):
			with conn.cursor() as curs:
				does_csid_exist = len(curs.execute("select from odt_changeset where csid = %s", (csid,))) == 1
		
		cs_comment = ""
		for tag in elem.iterchildren(tag='tag'):
			if tag.attrib['k'] == "comment":
				cs_comment = tag.attrib["v"]
		
		if not does_csid_exist:
			with conn.cursor() as curs:
				curs.execute("insert into odt_changeset (csid, uid, ts, username, comment) values (%s, %s, %s, %s, %s)", (csid, uid, ts, username, cs_comment))
				conn.commit()

		for discussion in elem.iterchildren(tag='discussion'):
			for commentElement in discussion.iterchildren(tag='comment'):
				comment_uid = commentElement.attrib.get('uid', '0')
				comment_username = commentElement.attrib.get('user', 'unknown')
				comment_ts = commentElement.attrib.get('date')
				for text in commentElement.iterchildren(tag='text'):
					comment_text = text.text
				with conn.cursor() as curs:
					curs.execute("insert into odt_comment (csid, uid, ts, username, comment) values (%s, %s, %s, %s, %s)", (csid, comment_uid, comment_ts, comment_username, comment_text))
					conn.commit()

		if((parsedCount % 10000) == 0):
			print(f"Processed {parsedCount} changesets")

		elem.clear()
	print(f'finished importing {parsedCount} records')

def doReplication(first_state, last_state, step=1):
	changesets = {}
	comments = {}
	for state in range(first_state, last_state, step):
		stateString = str(state)
		urlState = f'00{stateString[0]}/{stateString[1:4]}/{stateString[4:7]}'
		url = f'https://planet.openstreetmap.org/replication/changesets/{urlState}.osm.gz'
		with urllib.request.urlopen(url) as f:
			osmfile = gzip.open(BytesIO(f.read()))
			print(f'importing {urlState}')
			context = etree.iterparse(osmfile)
			next(context)
			for action, elem in context:
				if(elem.tag != 'changeset'):
					continue

				if (elem.attrib.get('closed_at', False) == False):
					continue

				csid = int(elem.attrib['id'])
				uid = elem.attrib.get('uid', '0')
				username = elem.attrib.get('user', 'unknown')
				ts = elem.attrib.get('closed_at')
				cs_comment = ""
				for tag in elem.iterchildren(tag='tag'):
					if tag.attrib['k'] == "comment":
						cs_comment = tag.attrib["v"]

				if csid not in changesets:
					changesets[csid] = {
						"uid": uid,
						"username": username,
						"ts": ts,
						"cs_comment": cs_comment
					}


				for discussion in elem.iterchildren(tag='discussion'):
					for commentElement in discussion.iterchildren(tag='comment'):
						comment_uid = commentElement.attrib.get('uid', '0')
						comment_username = commentElement.attrib.get('user', 'unknown')
						comment_ts = commentElement.attrib.get('date')
						for text in commentElement.iterchildren(tag='text'):
							comment_text = text.text
						hashtext = f'{csid}{comment_uid}{comment_ts}'
						comment_id = sha1(hashtext.encode()).hexdigest()
						if comment_id not in comments:
							comments[comment_id] = {
								"csid": csid,
								"comment_uid": comment_uid,
								"comment_username": comment_username,
								"comment_ts": comment_ts,
								"comment_text": comment_text
							}
			elem.clear()

	with conn.cursor() as curs:
		existing_csid_query = curs.execute("select csid from odt_changeset where csid = ANY(%s)", (list(changesets),)).fetchall()
		existing_csids = []
		for existing_csid in existing_csid_query:
			existing_csids.append(existing_csid["csid"])
		existing_comment_id_query = curs.execute("select comment_id from odt_comment where comment_id = ANY(%s)", (list(comments),)).fetchall()
		existing_comment_ids = []
		for existing_comment_id in existing_comment_id_query:
			existing_comment_ids.append(existing_comment_id["comment_id"])
		for csid, data in changesets.items():
			if csid not in existing_csids:
				curs.execute("insert into odt_changeset (csid, uid, ts, username, comment) values (%s, %s, %s, %s, %s)", (csid, data["uid"], data["ts"], data["username"], data["cs_comment"]))
		for comment_id, data in comments.items():
			if comment_id not in existing_comment_ids:
					curs.execute("insert into odt_comment (comment_id, csid, uid, ts, username, comment) values (%s, %s, %s, %s, %s, %s)", (comment_id, data["csid"], data["comment_uid"], data["comment_ts"], data["comment_username"], data["comment_text"]))
		conn.commit()
		
	print(f'finished importing {len(changesets)} changesets and {len(comments)} comments')

def doCron():
	with conn.cursor() as curs:
		curs.execute('select max_state from odt_state')
		max_state = curs.fetchone()["max_state"]
		with urllib.request.urlopen('https://planet.openstreetmap.org/replication/changesets/state.yaml') as f:
			state_file = f.read().decode().split('\n')[2]
			current_state = int(re.search('(\d+)', state_file)[1])
			if (max_state != current_state):
				print(f'importing state file {max_state} to {current_state}')
				doReplication(max_state, current_state+1)
				curs.execute('update odt_state set max_state = %s', (current_state,))
				conn.commit()
			else:
				print(f'{current_state} is the last state file available')

def doBackfill(number_to_backfill):
	with conn.cursor() as curs:
		curs.execute('select min_state from odt_state')
		min_state = curs.fetchone()["min_state"]
		new_min_state = min_state - number_to_backfill
		print(f'backfilling state files {min_state} to {new_min_state}')
		doReplication(min_state, new_min_state, -1)
		curs.execute('update odt_state set min_state = %s', (new_min_state,))
		conn.commit()


argparser = argparse.ArgumentParser(description="Import OSM Changesets from a file")
argparser.add_argument('-f', '--file', action='store', dest='fileName', help='OSM changeset file to import')
argparser.add_argument('-r', '--replication', action='store', dest='replication', help='OSM replication state number to import')
argparser.add_argument('-c', '--cron', action='store_true', dest='isCron', default=False, help='cron mode to import the next state files')
argparser.add_argument('-b', '--backfill', action='store', dest='toBackfill', nargs='?', const=1000, type=int, help='number of state files to backfill (default 1000)')

args = argparser.parse_args()

if (args.fileName):
	changesetFile = open(args.fileName, 'rb')
	parseFile(changesetFile, False)
elif (args.replication):
	doReplication(args.replication)
elif (args.isCron):
	doCron()
elif (args.toBackfill):
	doBackfill(args.toBackfill)