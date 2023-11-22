from datetime import datetime
from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from server import schema, conn
from strawberry.fastapi import GraphQLRouter


graphql_app = GraphQLRouter(schema)

app = FastAPI()

@app.get("/resolve", status_code=200)
async def resolve(response: Response, uid: int = 0, csid: int = 0, expires_at = None):
	if (uid == 0 or csid == 0):
		response.status_code = 400
	resolved_at = datetime.now()
	with conn.cursor() as curs:
		curs.execute('insert into odt_resolved (uid, csid, resolved_at, expires_at) values (%s,%s,%s,%s)', (uid, csid, resolved_at, expires_at))
		conn.commit()
	return {"message": f"{uid} has resolved {csid}"}

app.include_router(graphql_app, prefix="/graphql")

app.add_middleware(
	CORSMiddleware,
	allow_origins=["*"],
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)