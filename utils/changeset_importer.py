from datetime import datetime
import gzip
from io import BytesIO
import re
from lxml import etree
from hashlib import sha1
import os
import psycopg
import argparse
import urllib.request
import json
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
			ts = datetime.fromisoformat(elem.attrib.get('closed_at'))
			cs_tags = {}
			for tag in elem.iterchildren(tag='tag'):
				cs_tags[tag.attrib['k']] = tag.attrib['v']

			if csid not in changesets:
				changesets[csid] = {
					"uid": uid,
					"username": username,
					"ts": ts,
					"tags": cs_tags
				}


			for discussion in elem.iterchildren(tag='discussion'):
				for commentElement in discussion.iterchildren(tag='comment'):
					comment_uid = commentElement.attrib.get('uid', '0')
					comment_username = commentElement.attrib.get('user', 'unknown')
					comment_ts = datetime.fromisoformat(commentElement.attrib.get('date'))
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
		existing_comment_id_query = curs.execute("select id from odt_changeset_comment where id = ANY(%s)", (list(comments),)).fetchall()
		existing_comment_ids = []
		for existing_comment_id in existing_comment_id_query:
			existing_comment_ids.append(existing_comment_id["id"])
		for csid, data in changesets.items():
			if csid not in existing_csids:
				curs.execute("insert into odt_changeset (csid, uid, ts, username, last_activity_ts, last_activity_uid, tags) values (%s, %s, %s, %s, %s,%s,%s)", (csid, data["uid"], data["ts"], data["username"], data["ts"], data["uid"], json.dumps(data['tags'])))
				test_user_exists = curs.execute("select uid from odt_user where uid = %s", (data["uid"],)).fetchone()
				if not test_user_exists:
					curs.execute("insert into odt_user (uid,username) values (%s,%s)", (data["uid"], data["username"]))

		for comment_id, data in comments.items():
			if comment_id not in existing_comment_ids:
					# Add comment data to comment table
					curs.execute("insert into odt_changeset_comment (id, csid, uid, ts, username, text) values (%s, %s, %s, %s, %s, %s)", (comment_id, data["csid"], data["comment_uid"], data["comment_ts"], data["comment_username"], data["comment_text"]))
					test_user_exists = curs.execute("select uid from odt_user where uid = %s", (data["comment_uid"],)).fetchone()
					if not test_user_exists:
						curs.execute("insert into odt_user (uid,username) values (%s,%s)", (data["comment_uid"], data["comment_username"]))
					# Update changeset last_activity
					cs_activity = curs.execute('select last_activity_ts from odt_changeset where csid=%s', (data["csid"],)).fetchone()
					if data["comment_ts"] > cs_activity["last_activity_ts"]:
						curs.execute('update odt_changeset set last_activity_ts=%s, last_activity_uid=%s where csid=%s', (data["comment_ts"], data["comment_uid"], data["csid"]))

					og_changeset = changesets.get(data['csid'])
					if not og_changeset:
						print('Original changeset not found')
						continue

					# Get all users watching the changeset
					all_watching_users = curs.execute('select * from odt_watched_changesets where csid=%s', (data["csid"],))
					for user in all_watching_users.fetchall():
						if user["uid"] != int(data["comment_uid"]):
							curs.execute('update odt_watched_changesets set resolved_at = null, snooze_until = null where uid=%s and csid=%s', (data['comment_uid'], data['csid']))

					# Add changeset to comment author's watched list
					check_watched_for_comment_author = curs.execute('select * from odt_watched_changesets where uid=%s and csid=%s limit 1', (data['comment_uid'], data['csid'])).fetchone()
					if check_watched_for_comment_author and og_changeset["uid"] != data["comment_uid"]:
						curs.execute('update odt_watched_changesets set resolved_at = null, snooze_until = null where uid=%s and csid=%s', (data['comment_uid'], data['csid']))
					else:
						curs.execute('insert into odt_watched_changesets (uid, csid, resolved_at, snooze_until) values (%s,%s,null,null)', (data['comment_uid'], data['csid']))
					check_watched_for_changeset_author = curs.execute('select * from odt_watched_changesets where uid=%s and csid=%s limit 1', (og_changeset['uid'], data['csid'])).fetchone()
					if check_watched_for_changeset_author:
						curs.execute('update odt_watched_changesets set resolved_at = null, snooze_until = null where uid=%s and csid=%s', (og_changeset['uid'], data['csid']))
					else:
						curs.execute('insert into odt_watched_changesets (uid, csid, resolved_at, snooze_until) values (%s,%s,null,null)', (og_changeset['uid'], data['csid']))
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
argparser.add_argument('-c', '--cron', action='store', dest='isCron', nargs='?', const=100, type=int, help='cron mode to import the next number of state files, limited by the number specified (default limit 100)')

args = argparser.parse_args()

if (args.replication):
	doReplication(args.replication, args.replication+1)
if (args.isCron):
	doCron(args.isCron)