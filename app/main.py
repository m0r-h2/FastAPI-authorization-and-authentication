from fastapi import FastAPI

from app.routes import users, admin

app = FastAPI()

app.include_router(users.router)
app.include_router(admin.router)


@app.get("/")
async def hello():
    return {"message": "hello"}
