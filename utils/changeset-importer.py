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

DB_HOST = os.environ.get('DB_HOST', '127.0.0.1')
DB_PORT = os.environ.get('DB_PORT', 5432)
DB_NAME = os.environ.get('DB_NAME', 'odt')
DB_USER = os.environ.get('DB_USER', 'odt')
DB_PASS = os.environ.get('DB_PASS', 'odt')

conn = psycopg.connect(f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}", row_factory=dict_row)

def doReplication(first_state, last_state, step=1):
	changesets = {}
	comments = {}
	for state in range(first_state, last_state, step):
		stateString = str(state)
		urlState = f'00{stateString[0]}/{stateString[1:4]}/{stateString[4:7]}'
		url = f'https://planet.openstreetmap.org/replication/changesets/{urlState}.osm.gz'
		f = urllib.request.urlopen(url, timeout=10)
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
				curs.execute("insert into odt_changeset (csid, uid, ts, username, comment, last_activity) values (%s, %s, %s, %s, %s,%s)", (csid, data["uid"], data["ts"], data["username"], data["cs_comment"], data["ts"]))
		for comment_id, data in comments.items():
			if comment_id not in existing_comment_ids:
					curs.execute("insert into odt_comment (comment_id, csid, uid, ts, username, comment) values (%s, %s, %s, %s, %s, %s)", (comment_id, data["csid"], data["comment_uid"], data["comment_ts"], data["comment_username"], data["comment_text"]))
					cs_activity = curs.execute('select last_activity from odt_changeset where csid=%s', (data["csid"],)).fetchone()
					if not cs_activity["last_activity"] or data["comment_ts"] > cs_activity["last_activity"]:
						curs.execute('update odt_changeset set last_activity=%s where csid=%s', (data["comment_ts"], data["csid"]))
		conn.commit()
		
	print(f'finished importing {len(changesets)} changesets and {len(comments)} comments')

def doCron(limit = 1000):
	with conn.cursor() as curs:
		curs.execute('select max_state from odt_state')
		old_max_state = curs.fetchone()["max_state"]
		with urllib.request.urlopen('https://planet.openstreetmap.org/replication/changesets/state.yaml') as f:
			state_file = f.read().decode().split('\n')[2]
			planet_current_state = int(re.search(r'(\d+)', state_file)[1])
			if (planet_current_state != old_max_state):
				new_max_state = planet_current_state
				if (old_max_state + limit < planet_current_state):
					new_max_state = old_max_state + limit
				print(f'importing state file {old_max_state+1} to {new_max_state}')
				doReplication(old_max_state+1, new_max_state+1)
				curs.execute('update odt_state set max_state = %s', (new_max_state,))
				conn.commit()
			else:
				print(f'{planet_current_state} is the last state file available')


argparser = argparse.ArgumentParser(description="Import OSM Changeset replication files")
argparser.add_argument('-r', '--replication', action='store', dest='replication', type=int, help='OSM replication state number to import')
argparser.add_argument('-c', '--cron', action='store', dest='isCron', nargs='?', const=1000, type=int, help='cron mode to import the next number of state files, limited by the number specified (default limit 1000)')

args = argparser.parse_args()

if (args.replication):
	doReplication(args.replication, args.replication+1)
if (args.isCron):
	doCron(args.isCron)