import gzip
from io import BytesIO
import re
from lxml import etree
import os
import psycopg
import argparse
import urllib.request

conn = psycopg.connect(f"postgresql://{os.environ.get('DB_USER')}:{os.environ.get('DB_PASS')}@{os.environ.get('DB_HOST')}:{os.environ.get('DB_PORT')}/{os.environ.get('DB_NAME')}")

def parseFile(changesetFile, doReplication):
	parsedCount = 0
	print('starting import')
	context = etree.iterparse(changesetFile)
	next(context)
	for action, elem in context:
		if(elem.tag != 'changeset'):
			continue

		if (elem.attrib.get('closed_at', False) == False):
			continue

		parsedCount += 1

		csid = elem.attrib['id']
		uid = elem.attrib.get('uid', '')
		username = elem.attrib.get('user', '')
		ts = elem.attrib.get('closed_at')

		if(doReplication):
			with conn.cursor() as curs:
				curs.execute("delete from odt_changeset where csid = %s", (csid,))
				curs.execute("delete from odt_comment where csid = %s", (csid,))
				conn.commit()
		
		cs_comment = ""
		for tag in elem.iterchildren(tag='tag'):
			if tag.attrib['k'] == "comment":
				cs_comment = tag.attrib["v"]
		
		with conn.cursor() as curs:
			curs.execute("insert into odt_changeset (csid, uid, ts, username, comment) values (%s, %s, %s, %s, %s)", (csid, uid, ts, username, cs_comment))
			conn.commit()

		for discussion in elem.iterchildren(tag='discussion'):
			for commentElement in discussion.iterchildren(tag='comment'):
				comment_uid = commentElement.attrib.get('uid')
				comment_username = commentElement.attrib.get('user')
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

def doReplication(stateNum):
	urlState = f'00{stateNum[0]}/{stateNum[1:4]}/{stateNum[4:7]}'
	print(urlState)
	url = f'https://planet.openstreetmap.org/replication/changesets/{urlState}.osm.gz'
	with urllib.request.urlopen(url) as f:
		osmfile = gzip.open(BytesIO(f.read()))
		parseFile(osmfile, True)

def doCron():
	with conn.cursor() as curs:
		curs.execute('select last_state from odt_state')
		last_state = curs.fetchone()[0]
		with urllib.request.urlopen('https://planet.openstreetmap.org/replication/changesets/state.yaml') as f:
			state_file = f.read().decode().split('\n')[2]
			current_state = int(re.search('(\d+)', state_file)[1])
			if (last_state != current_state):
				print(f'importing state file {last_state} to {current_state}')
				for state in range(last_state, current_state+1):
					doReplication(str(state))
			else:
				print(f'{last_state} is the last state file available')
		curs.execute('update odt_state set last_state = %s', (current_state,))
		conn.commit()


argparser = argparse.ArgumentParser(description="Import OSM Changesets from a file")
argparser.add_argument('-f', '--file', action='store', dest='fileName', help='OSM changeset file to import')
argparser.add_argument('-r', '--replication', action='store', dest='replication', help='OSM replication state number to import')
argparser.add_argument('-c', '--cron', action='store_true', dest='isCron', default=False, help='cron mode to import the next state files')

args = argparser.parse_args()

if (args.fileName):
	changesetFile = open(args.fileName, 'rb')
	parseFile(changesetFile, False)
elif (args.replication):
	doReplication(args.replication)
elif (args.isCron):
	doCron()