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
		odt_changeset.last_activity as last_activity
	from odt_changeset
	left join odt_comment
		on odt_changeset.csid = odt_comment.csid
	where
		odt_comment.uid = %s and
		not odt_changeset.csid = ANY(%s)
	order by odt_changeset.last_activity desc limit %s offset %s
'''

all_resolved_cs_query = '''
	select
		odt_changeset.csid as csid,
		odt_resolved.resolved_at as resolved_at
	from odt_resolved
	left join odt_changeset
		on odt_changeset.csid = odt_resolved.csid
	where
		odt_resolved.uid = %s

'''

def get_watched_changesets(uid: int, limit: int, offset: int) -> typing.List["Changeset"]:
	all_changesets = []
	print(offset*20)
	with conn.cursor() as curs:
		all_resolved_query = curs.execute(all_resolved_cs_query, (uid,))
		all_resolved_cs =  []
		for resolved_cs in all_resolved_query.fetchall():
			all_resolved_cs.append(resolved_cs["csid"])
		all_changeset_query = curs.execute(all_watched_cs_query, (uid,all_resolved_cs,limit,offset*20))
		all_watched_cs =  all_changeset_query.fetchall()
		for changeset in all_watched_cs:
			if changeset["csid"] in all_resolved_cs:
				print(changeset["csid"])
				continue
			all_comments = curs.execute('select uid,ts from odt_comment where csid=%s order by ts asc', (changeset["csid"],)).fetchall()
			owner_last_response = datetime.fromtimestamp(0)
			our_last_response = datetime.fromtimestamp(0)
			for comment in all_comments:
				if comment["uid"] == changeset["uid"]:
					owner_last_response = comment["ts"]
				if comment["uid"] == uid:
					our_last_response = comment["ts"]
			if owner_last_response > our_last_response:
				has_response = True
			else:
				has_response = False
			user_last_changeset = curs.execute('select csid, ts from odt_changeset where uid=%s order by ts desc', (changeset["uid"],)).fetchone()
			if user_last_changeset["ts"] > our_last_response:
				has_new_changesets = True
			else:
				has_new_changesets = False

			all_changesets.append(
				Changeset(
					csid=changeset["csid"],
					lastActivity=changeset["last_activity"],
					username = changeset["username"],
					ts=changeset["ts"],
					hasResponse=has_response,
					hasNewChangesets=has_new_changesets
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
			is_resolved = curs.execute('select * from odt_resolved where csid=%s and uid = %s', (csid, uid)).fetchone()
			status = "Unresolved"
			if is_resolved:
				if is_resolved["expires_at"]:
					status = f"Snoozed until {is_resolved['expires_at']}"
				else:
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
	ts: datetime
	hasResponse: bool
	hasNewChangesets: bool

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
	uid: int = 0
	csid: int = 0
	status: str
	expiresAt: object | None = None

@app.post("/resolve", status_code=200)
async def resolve(resolve: Resolve, response: Response):
	if (resolve.uid == 0 or resolve.csid == 0):
		response.status_code = 400
		return response
	resolved_at = datetime.utcnow()
	with conn.cursor() as curs:
		is_existing = curs.execute('select * from odt_resolved where uid=%s and csid=%s', (resolve.uid, resolve.csid)).fetchone()
		if is_existing:
			if resolve.expiresAt:
				curs.execute('update odt_resolved set expires_at = %s where uid=%s and csid=%s', (resolve.expiresAt, resolve.uid, resolve.csid))
			else:
				curs.execute('update odt_resolved set expires_at = null where uid=%s and csid=%s', (resolve.uid, resolve.csid))
		else:
			curs.execute('insert into odt_resolved (uid, csid, resolved_at, expires_at) values (%s,%s,%s,%s)', (resolve.uid, resolve.csid, resolved_at, resolve.expiresAt))
		conn.commit()
	return {"message": resolve}

@app.post("/unresolve", status_code=200)
async def resolve(unresolve: Resolve, response: Response):
	if (unresolve.uid == 0 or unresolve.csid == 0):
		response.status_code = 400
		return response
	with conn.cursor() as curs:
		curs.execute('delete from odt_resolved where uid=%s and csid=%s', (unresolve.uid, unresolve.csid))
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