import os
import psycopg
import strawberry
import typing

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
		odt_changeset.comment as comment
	from odt_changeset
	left join odt_comment
		on odt_changeset.csid = odt_comment.csid
	where
		odt_comment.uid = %s
	order by odt_changeset.csid desc
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

def get_watched_changesets(uid: int) -> typing.List["Changeset"]:
	all_changesets = []
	with conn.cursor() as curs:
		all_changeset_query = curs.execute(all_watched_cs_query, (uid,))
		all_watched_cs =  all_changeset_query.fetchall()
		all_resolved_query = curs.execute(all_resolved_cs_query, (uid,))
		all_resolved_cs =  []
		for resolved_cs in all_resolved_query.fetchall():
			all_resolved_cs.append(resolved_cs["csid"])
		for changeset in all_watched_cs:
			if changeset["csid"] in all_resolved_cs:
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
					lastActivity=all_comments[0]["ts"],
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

def get_changeset_details(csid: int) -> "FullChangeset":
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
			full_changeset = FullChangeset(
				csid=changeset["csid"],
				uid=changeset["uid"],
				username = changeset["username"],
				ts=changeset["ts"],
				comment=changeset["comment"],
				discussion=all_comments
			)
			return full_changeset


@strawberry.type
class Changeset:
	csid: int
	lastActivity: datetime
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

@strawberry.type
class Query:
	watched_changesets: typing.List["Changeset"] = strawberry.field(resolver=get_watched_changesets)
	get_changeset_comments: typing.List["Comment"] = strawberry.field(resolver=get_changeset_comments)
	get_changeset_details: "FullChangeset" = strawberry.field(resolver=get_changeset_details)

schema = strawberry.Schema(query=Query)