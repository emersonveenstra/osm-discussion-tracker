from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from server import schema
from strawberry.fastapi import GraphQLRouter


graphql_app = GraphQLRouter(schema)

app = FastAPI()
app.include_router(graphql_app, prefix="/graphql")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)