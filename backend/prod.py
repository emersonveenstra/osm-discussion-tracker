from datetime import datetime
from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from server import schema, conn
from strawberry.fastapi import GraphQLRouter


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