from fastapi import FastAPI 
from fastapi.middleware.cors import CORSMiddleware


app=FastAPI()
from routes.upload import router
from routes.documents import routerd
from routes.chat import routerc
from routes.query import routerq
from routes.message import routerm
from routes.user import routeru

app.include_router(router)

app.include_router(routerd)
app.include_router(routerc)
app.include_router(routerq)
app.include_router(routerm)
app.include_router(routeru)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get('/')
def home():
    return "hello world"
