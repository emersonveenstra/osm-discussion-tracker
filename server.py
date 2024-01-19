import json
import os
from typing import Annotated
import psycopg
import strawberry
from datetime import datetime
from fastapi import FastAPI, Header, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from strawberry.fastapi import GraphQLRouter
from strawberry.extensions import AddValidationRules
from graphql.validation import NoSchemaIntrospectionCustomRule
import urllib.request

from datetime import datetime
from psycopg.rows import dict_row

DB_HOST = os.environ.get('DB_HOST', '127.0.0.1')
DB_PORT = os.environ.get('DB_PORT', 5432)
DB_NAME = os.environ.get('DB_NAME', 'odt')
DB_USER = os.environ.get('DB_USER', 'odt')
DB_PASS = os.environ.get('DB_PASS', 'odt')

@strawberry.type
class Changeset:
	csid: int
	uid: int
	lastActivityTs: datetime
	username: str
	ts: datetime
	notices: list[str]
	comment: str
	status: str

@strawberry.type
class Comment:
	csid: int
	uid: int
	username: str
	ts: datetime
	text: str

@strawberry.type
class ChangesetNote:
	csid: int
	username: str
	ts: datetime
	text: str

@strawberry.type
class ChangesetFlag:
	csid: int
	username: str
	ts: datetime
	text: str

@strawberry.type
class FullChangeset:
	csid: int
	uid: int
	username: str
	ts: datetime
	csComment: str
	notices: list[str]
	comments: list["Comment"]
	notes: list["ChangesetNote"]
	flags: list["ChangesetFlag"]
	status: str
	statusDate: datetime | None

conn_string = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

all_watched_cs_query = '''
	select distinct
		odt_changeset.csid as csid,
		odt_changeset.uid as uid,
		odt_changeset.username as username,
		odt_changeset.ts as ts,
		odt_changeset.last_activity_ts as last_activity_ts,
		odt_changeset.last_activity_uid as last_activity_uid,
		odt_changeset.tags as tags,
		odt_watched_changesets.resolved_at as resolved_at,
		odt_watched_changesets.snooze_until as snooze_until
	from odt_changeset
	left join odt_watched_changesets
		on odt_changeset.csid = odt_watched_changesets.csid
	where
		odt_watched_changesets.uid = %s
		{}
	order by odt_changeset.last_activity_ts desc
'''

def get_watched_changesets(uid: int, showWatched: bool, showSnoozed: bool, showResolved: bool) -> list[Changeset]:
	all_changesets = []
	with psycopg.connect(conn_string, row_factory=dict_row) as conn:
		query_filter = ''
		if showWatched:
			if not showSnoozed:
				if not showResolved:
					query_filter = 'and odt_watched_changesets.snooze_until is null and odt_watched_changesets.resolved_at is null'
				else:
					query_filter = 'and odt_watched_changesets.snooze_until is null'
			elif not showResolved:
				query_filter = 'and odt_watched_changesets.resolved_at is null'
			else:
				query_filter = ''
		elif showSnoozed:
			if not showResolved:
				query_filter = 'and odt_watched_changesets.snooze_until is not null and odt_watched_changesets.resolved_at is null'
			else:
				query_filter = 'and odt_watched_changesets.snooze_until is not null or odt_watched_changesets.resolved_at is not null'
		elif showResolved:
			query_filter = 'and odt_watched_changesets.resolved_at is not null'

		all_changeset_query = conn.execute(all_watched_cs_query.format(query_filter), (uid,))
		all_watched_cs =  all_changeset_query.fetchall()
		tags_to_keep = ['comment']
		for changeset in all_watched_cs:
			comment = changeset["tags"].get("comment", "")
			notices = []
			if changeset["last_activity_uid"] != uid:
				notices.append('Has Response')

			if changeset["resolved_at"]:
				status = "resolved"
			elif changeset["snooze_until"]:
				status = "snoozed"
			else:
				status = "watched"

			all_changesets.append(
				Changeset(
					csid=changeset["csid"],
					lastActivityTs=changeset["last_activity_ts"],
					username = changeset["username"],
					uid = changeset["uid"],
					ts=changeset["ts"],
					notices=notices,
					comment=comment,
					status=status
				)
			)
	return all_changesets

def get_changeset_details(csid: int, uid: int) -> FullChangeset:
	all_comments = []
	all_notes = []
	all_flags = []
	with psycopg.connect(conn_string, row_factory=dict_row) as conn:
		all_comment_query = conn.execute('select * from odt_changeset_comment where csid = %s order by ts asc', (csid,))
		for changeset in all_comment_query.fetchall():
			all_comments.append(
				Comment(
					csid=changeset["csid"],
					uid=changeset["uid"],
					username = changeset["username"],
					ts=changeset["ts"],
					text=changeset["text"],
				)
			)
		all_note_query = conn.execute('select * from odt_changeset_note where csid = %s order by ts asc', (csid,))
		for note in all_note_query.fetchall():
			if (note['isflag']):
				all_flags.append(
					ChangesetFlag(
						csid=note["csid"],
						username=note["username"],
						ts=note["ts"],
						text=note["text"],
					)
				)
			else:
				all_notes.append(
					ChangesetNote(
						csid=note["csid"],
						username=note["username"],
						ts=note["ts"],
						text=note["text"],
					)
				)
			
		all_changeset_query = conn.execute('select * from odt_changeset where csid = %s', (csid,))
		changeset = all_changeset_query.fetchone()
		if changeset:
			is_resolved = conn.execute('select * from odt_watched_changesets where csid=%s and uid = %s', (csid, uid)).fetchone()
			status = "unwatched"
			statusDate = None
			csComment = changeset["tags"].get("comment", "")
			if is_resolved:
				if is_resolved["snooze_until"]:
					status = "snoozed"
					statusDate = is_resolved['snooze_until']
				elif is_resolved["resolved_at"]:
					status = "resolved"
				else:
					status = "watched"
			full_changeset = FullChangeset(
				csid=changeset["csid"],
				uid=changeset["uid"],
				username = changeset["username"],
				ts=changeset["ts"],
				csComment=csComment,
				notices=[],
				comments=all_comments,
				notes=all_notes,
				flags=all_flags,
				status=status,
				statusDate=statusDate
			)
			return full_changeset

@strawberry.type
class Query:
	watched_changesets: list[Changeset] = strawberry.field(resolver=get_watched_changesets)
	get_changeset_details: FullChangeset = strawberry.field(resolver=get_changeset_details)

schema = strawberry.Schema(query=Query, extensions=[
	AddValidationRules([NoSchemaIntrospectionCustomRule])
])

graphql_app = GraphQLRouter(schema, graphql_ide=None)

app = FastAPI()

class ResolveStatus(BaseModel):
	uid: int
	csid: list[int] = []
	status: str
	snoozeUntil: str = ''

class ResolveChangesetNote(BaseModel):
	username: str
	csid: int
	note: str
	isFlag: bool

@app.post("/status", status_code=200)
async def changeStatus(resolve: ResolveStatus, response: Response):
	print(resolve)
	for csid in resolve.csid:
		with psycopg.connect(conn_string, row_factory=dict_row) as conn:
			is_existing = conn.execute('select * from odt_watched_changesets where uid=%s and csid=%s', (resolve.uid, csid)).fetchone()
			if is_existing:
				if resolve.status == 'snoozed':
					conn.execute('update odt_watched_changesets set snooze_until = %s where uid=%s and csid=%s', (resolve.snoozeUntil, resolve.uid, csid))
				elif resolve.status == 'resolved':
					conn.execute('update odt_watched_changesets set resolved_at = %s, snooze_until = null where uid=%s and csid=%s', (datetime.utcnow(), resolve.uid, csid))
				elif resolve.status == 'watched':
					conn.execute('update odt_watched_changesets set resolved_at = null, snooze_until = null where uid=%s and csid=%s', (resolve.uid, csid))
				elif resolve.status == 'unwatched':
					conn.execute('delete from odt_watched_changesets where uid=%s and csid=%s', (resolve.uid, csid))
			else:
				if resolve.status == 'snoozed':
					conn.execute('insert into odt_watched_changesets (uid, csid, snooze_until) values (%s,%s,%s)', (resolve.uid, csid, resolve.snoozeUntil))
				elif resolve.status == 'resolved':
					conn.execute('insert into odt_watched_changesets (uid, csid, resolved_at) values (%s,%s,%s)', (resolve.uid, csid, datetime.utcnow()))
				elif resolve.status == 'watched':
					conn.execute('insert into odt_watched_changesets (uid, csid) values (%s,%s)', (resolve.uid, csid))
	return {"message": resolve}

@app.post('/addChangesetNote', status_code=200)
async def addChangesetNote(resolve: ResolveChangesetNote, response: Response, authorization: Annotated[str | None, Header()] = None):
	print(resolve, authorization)
	check_headers = urllib.request.Request('https://www.openstreetmap.org/api/0.6/user/details.json')
	check_headers.add_header('Authorization', authorization)
	with urllib.request.urlopen(check_headers) as f:
		real_username = json.loads(f.read().decode('utf-8'))["user"]["display_name"]
		print(real_username)
	with psycopg.connect(conn_string, row_factory=dict_row) as conn:
		is_existing = conn.execute('select * from odt_changeset_note where username=%s and csid=%s and text=%s and isFlag=%s', (resolve.username, resolve.csid, resolve.note, resolve.isFlag)).fetchone()
		if not is_existing:
			conn.execute('insert into odt_changeset_note (username,csid,ts,text,isFlag) values (%s,%s,%s,%s,%s)', (resolve.username, resolve.csid, datetime.utcnow(), resolve.note, resolve.isFlag))
			if resolve.isFlag:
				conn.execute("update odt_changeset set tags = JSONB_SET(tags, '{flagged}', %s) where csid=%s", (True, resolve.csid))

app.include_router(graphql_app, prefix="/graphql")

app.add_middleware(
	CORSMiddleware,
	allow_origins=["*"],
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)