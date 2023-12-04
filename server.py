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
	print(showWatched, showSnoozed, showResolved)
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
			if last_comment["uid"] != uid:
				has_response = True
			else:
				has_response = False
			user_last_changeset = curs.execute('select csid, ts from odt_changeset where uid=%s order by ts desc limit 1', (changeset["uid"],)).fetchone()
			if user_last_changeset["ts"] > last_comment["ts"]:
				has_new_changesets = True
			else:
				has_new_changesets = False

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
					hasNewChangesets=has_new_changesets,
					status=status
				)
			)
	return all_changesets

def get_changeset_comments(csid: int) -> typing.List["Comment"]:
	all_comments = []
	with conn.cursor() as curs:
		all_changeset_query = curs.execute('select * from odt_comment where csid = %s order by ts asc', (csid,))
		for changeset in all_changeset_query.fetchall():
			all_comments.append(
				Comment(
					csid=changeset["csid"],
					uid=changeset["uid"],
					username = changeset["username"],
					ts=changeset["ts"],
					comment=changeset["comment"]
				)
			)
	return all_comments

def get_changeset_details(csid: int, uid: int) -> "FullChangeset":
	all_comments = []
	with conn.cursor() as curs:
		all_comment_query = curs.execute('select * from odt_comment where csid = %s order by ts asc', (csid,))
		for changeset in all_comment_query.fetchall():
			all_comments.append(
				Comment(
					csid=changeset["csid"],
					uid=changeset["uid"],
					username = changeset["username"],
					ts=changeset["ts"],
					comment=changeset["comment"]
				)
			)
		all_changeset_query = curs.execute('select * from odt_changeset where csid = %s', (csid,))
		changeset = all_changeset_query.fetchone()
		if changeset:
			is_resolved = curs.execute('select * from odt_watched where csid=%s and uid = %s', (csid, uid)).fetchone()
			status = "Watching"
			if is_resolved:
				if is_resolved["snooze_until"]:
					status = f"Snoozed until {is_resolved['snooze_until']}"
				elif is_resolved["resolved_at"]:
					status = "Resolved"
			full_changeset = FullChangeset(
				csid=changeset["csid"],
				uid=changeset["uid"],
				username = changeset["username"],
				ts=changeset["ts"],
				comment=changeset["comment"],
				discussion=all_comments,
				status=status
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
	hasNewChangesets: bool
	status: str

@strawberry.type
class Comment:
	csid: int
	uid: int
	username: str
	ts: datetime
	comment: str

@strawberry.type
class FullChangeset:
	csid: int
	uid: int
	username: str
	ts: datetime
	comment: str
	discussion: typing.List["Comment"]
	status: str

@strawberry.type
class Query:
	watched_changesets: typing.List["Changeset"] = strawberry.field(resolver=get_watched_changesets)
	get_changeset_comments: typing.List["Comment"] = strawberry.field(resolver=get_changeset_comments)
	get_changeset_details: "FullChangeset" = strawberry.field(resolver=get_changeset_details)

schema = strawberry.Schema(query=Query)

graphql_app = GraphQLRouter(schema)

app = FastAPI()

class Resolve(BaseModel):
	uid: int
	csid: list[int] = []
	status: str
	expiresAt: str | None = None
	snoozeUntil: str | None = None

@app.post("/resolve", status_code=200)
async def resolve(resolve: Resolve, response: Response):
	print(resolve)
	resolved_at = datetime.utcnow()
	for csid in resolve.csid:
		with conn.cursor() as curs:
			is_existing = curs.execute('select * from odt_watched where uid=%s and csid=%s', (resolve.uid, csid)).fetchone()
			if is_existing:
				if resolve.status == 'snooze':
					curs.execute('update odt_watched set snooze_until = %s where uid=%s and csid=%s', (resolve.snoozeUntil, resolve.uid, csid))
				else:
					curs.execute('update odt_watched set resolved_at = %s, snooze_until = null where uid=%s and csid=%s', (resolved_at, resolve.uid, csid))
			else:
				if resolve.status == 'snooze':
					curs.execute('insert into odt_watched (uid, csid, snooze_until) values (%s,%s,%s)', (resolve.uid, csid, resolve.snoozeUntil))
				else:
					curs.execute('insert into odt_watched (uid, csid, resolved_at) values (%s,%s,%s)', (resolve.uid, csid, resolved_at))
			conn.commit()
	return {"message": resolve}

@app.post("/unresolve", status_code=200)
async def resolve(unresolve: Resolve, response: Response):
	for csid in unresolve.csid:
		with conn.cursor() as curs:
			curs.execute('update odt_watched set snooze_until = null, resolved_at = null where uid=%s and csid=%s', (unresolve.uid, csid))
			conn.commit()
	return {"message": f"{unresolve.uid} has unresolved {unresolve.csid}"}

app.include_router(graphql_app, prefix="/graphql")

app.add_middleware(
	CORSMiddleware,
	allow_origins=["*"],
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)