import os
import psycopg
import strawberry
import typing
from datetime import datetime
from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from strawberry.fastapi import GraphQLRouter

from datetime import datetime
from psycopg.rows import dict_row

DB_HOST = os.environ.get('DB_HOST', '127.0.0.1')
DB_PORT = os.environ.get('DB_PORT', 5432)
DB_NAME = os.environ.get('DB_NAME', 'odt')
DB_USER = os.environ.get('DB_USER', 'odt')
DB_PASS = os.environ.get('DB_PASS', 'odt')

conn = psycopg.connect(f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}", row_factory=dict_row)

all_watched_cs_query = '''
	select distinct
		odt_changeset.csid as csid,
		odt_changeset.uid as uid,
		odt_changeset.username as username,
		odt_changeset.ts as ts,
		odt_changeset.comment as comment,
		odt_changeset.last_activity as last_activity,
		odt_watched.resolved_at as resolved_at,
		odt_watched.snooze_until as snooze_until
	from odt_changeset
	left join odt_watched
		on odt_changeset.csid = odt_watched.csid
	where
		odt_watched.uid = %s
		{}
	order by odt_changeset.last_activity desc
'''

def get_watched_changesets(uid: int, showWatched: bool, showSnoozed: bool, showResolved: bool) -> typing.List["Changeset"]:
	all_changesets = []
	with conn.cursor() as curs:
		query_filter = ''
		if showWatched:
			if not showSnoozed:
				if not showResolved:
					query_filter = 'and odt_watched.snooze_until is null and odt_watched.resolved_at is null'
				else:
					query_filter = 'and odt_watched.snooze_until is null'
			elif not showResolved:
				query_filter = 'and odt_watched.resolved_at is null'
			else:
				query_filter = ''
		elif showSnoozed:
			if not showResolved:
				query_filter = 'and odt_watched.snooze_until is not null and odt_watched.resolved_at is null'
			else:
				query_filter = 'and odt_watched.snooze_until is not null or odt_watched.resolved_at is not null'
		elif showResolved:
			query_filter = 'and odt_watched.resolved_at is not null'

		all_changeset_query = curs.execute(all_watched_cs_query.format(query_filter), (uid,))
		all_watched_cs =  all_changeset_query.fetchall()
		for changeset in all_watched_cs:
			last_comment = curs.execute('select uid,ts from odt_comment where csid=%s order by ts desc limit 1', (changeset["csid"],)).fetchone()
			if last_comment and last_comment["uid"] != uid:
				has_response = True
			else:
				has_response = False

			if changeset["resolved_at"]:
				status = "resolved"
			elif changeset["snooze_until"]:
				status = "snoozed"
			else:
				status = "watching"

			all_changesets.append(
				Changeset(
					csid=changeset["csid"],
					lastActivity=changeset["last_activity"],
					username = changeset["username"],
					comment=changeset["comment"],
					ts=changeset["ts"],
					hasResponse=has_response,
					status=status
				)
			)
	return all_changesets

def get_changeset_details(csid: int, uid: int) -> "FullChangeset":
	all_comments = []
	all_notes = []
	all_flags = []
	with conn.cursor() as curs:
		all_comment_query = curs.execute('select * from odt_comment where csid = %s order by ts asc', (csid,))
		for changeset in all_comment_query.fetchall():
			all_comments.append(
				Comment(
					csid=changeset["csid"],
					uid=changeset["uid"],
					username = changeset["username"],
					ts=changeset["ts"],
					comment=changeset["comment"],
				)
			)
		all_note_query = curs.execute('select * from odt_changeset_note where csid = %s order by ts asc', (csid,))
		for note in all_note_query.fetchall():
			if (note['isflag']):
				all_flags.append(
					ChangesetFlag(
						csid=note["csid"],
						username=note["username"],
						ts=note["ts"],
						note=note["note"],
					)
				)
			else:
				all_notes.append(
					ChangesetNote(
						csid=note["csid"],
						username=note["username"],
						ts=note["ts"],
						note=note["note"],
					)
				)
			
		all_changeset_query = curs.execute('select * from odt_changeset where csid = %s', (csid,))
		changeset = all_changeset_query.fetchone()
		if changeset:
			is_resolved = curs.execute('select * from odt_watched where csid=%s and uid = %s', (csid, uid)).fetchone()
			status = "unwatched"
			statusDate = None
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
				csComment=changeset["comment"],
				comments=all_comments,
				notes=all_notes,
				flags=all_flags,
				status=status,
				statusDate=statusDate
			)
			return full_changeset


@strawberry.type
class Changeset:
	csid: int
	lastActivity: datetime | None
	username: str
	comment: str
	ts: datetime
	hasResponse: bool
	status: str

@strawberry.type
class Comment:
	csid: int
	uid: int
	username: str
	ts: datetime
	comment: str

@strawberry.type
class ChangesetNote:
	csid: int
	username: str
	ts: datetime
	note: str

@strawberry.type
class ChangesetFlag:
	csid: int
	username: str
	ts: datetime
	note: str

@strawberry.type
class FullChangeset:
	csid: int
	uid: int
	username: str
	ts: datetime
	csComment: str
	comments: typing.List["Comment"]
	notes: typing.List["ChangesetNote"]
	flags: typing.List["ChangesetFlag"]
	status: str
	statusDate: datetime | None

@strawberry.type
class Query:
	watched_changesets: typing.List["Changeset"] = strawberry.field(resolver=get_watched_changesets)
	get_changeset_details: "FullChangeset" = strawberry.field(resolver=get_changeset_details)

schema = strawberry.Schema(query=Query)

graphql_app = GraphQLRouter(schema)

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
		with conn.cursor() as curs:
			is_existing = curs.execute('select * from odt_watched where uid=%s and csid=%s', (resolve.uid, csid)).fetchone()
			if is_existing:
				if resolve.status == 'snoozed':
					curs.execute('update odt_watched set snooze_until = %s where uid=%s and csid=%s', (resolve.snoozeUntil, resolve.uid, csid))
				elif resolve.status == 'resolved':
					curs.execute('update odt_watched set resolved_at = %s, snooze_until = null where uid=%s and csid=%s', (datetime.utcnow(), resolve.uid, csid))
				elif resolve.status == 'unwatched':
					curs.execute('delete from odt_watched where uid=%s and csid=%s', (resolve.uid, csid))
			else:
				if resolve.status == 'snoozed':
					curs.execute('insert into odt_watched (uid, csid, snooze_until) values (%s,%s,%s)', (resolve.uid, csid, resolve.snoozeUntil))
				elif resolve.status == 'resolved':
					curs.execute('insert into odt_watched (uid, csid, resolved_at) values (%s,%s,%s)', (resolve.uid, csid, datetime.utcnow()))
				elif resolve.status == 'watched':
					curs.execute('insert into odt_watched (uid, csid) values (%s,%s)', (resolve.uid, csid))
			conn.commit()
	return {"message": resolve}

@app.post('/addChangesetNote', status_code=200)
async def addChangesetNote(resolve: ResolveChangesetNote, response: Response):
	print(resolve)
	with conn.cursor() as curs:
		is_existing = curs.execute('select * from odt_changeset_note where username=%s and csid=%s and note=%s and isFlag=%s', (resolve.username, resolve.csid, resolve.note, resolve.isFlag)).fetchone()
		if not is_existing:
			curs.execute('insert into odt_changeset_note (username,csid,ts,note,isFlag) values (%s,%s,%s,%s,%s)', (resolve.username, resolve.csid, datetime.utcnow(), resolve.note, resolve.isFlag))

app.include_router(graphql_app, prefix="/graphql")

app.add_middleware(
	CORSMiddleware,
	allow_origins=["*"],
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)