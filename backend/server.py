import os
import psycopg
import strawberry
import typing

from datetime import datetime
from psycopg.rows import dict_row

conn = psycopg.connect(f"postgresql://{os.environ.get('DB_USER')}:{os.environ.get('DB_PASS')}@{os.environ.get('DB_HOST')}:{os.environ.get('DB_PORT')}/{os.environ.get('DB_NAME')}", row_factory=dict_row)

def get_watched_changesets(uid: int) -> typing.List["Changeset"]:
	all_changesets = []
	with conn.cursor() as curs:
		all_changeset_query = curs.execute('select distinct odt_changeset.csid as csid, odt_changeset.uid as uid, odt_changeset.username as username, odt_changeset.ts as ts, odt_changeset.comment as comment from odt_changeset left join odt_comment on odt_changeset.csid = odt_comment.csid where odt_comment.uid = %s order by odt_changeset.csid desc', (uid,))
		for changeset in all_changeset_query.fetchall():
			last_activity_ts = curs.execute('select ts from odt_comment where csid=%s order by ts desc', (changeset["csid"],)).fetchone()
			has_response_from_owner = curs.execute('select ts from odt_comment where csid=%s and uid=%s order by ts desc', (changeset["csid"], changeset["uid"])).fetchone()
			if has_response_from_owner:
				has_response = True
			else:
				has_response = False

			all_changesets.append(
				Changeset(
					csid=changeset["csid"],
					lastActivity=last_activity_ts["ts"],
					username = changeset["username"],
					ts=changeset["ts"],
					hasResponse=has_response
				)
			)
	return all_changesets

def get_changeset_comments(csid: int) -> typing.List["Comment"]:
	all_comments = []
	with conn.cursor() as curs:
		all_changeset_query = curs.execute('select * from odt_comment where csid = %s', (csid,))
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
		all_comment_query = curs.execute('select * from odt_comment where csid = %s', (csid,))
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