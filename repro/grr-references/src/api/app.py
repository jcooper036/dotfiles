from fastapi import Depends, FastAPI

from api.auth import identity

app = FastAPI()


@app.get("/a")
def a(user: str = Depends(identity)) -> str:
    return user


@app.get("/b")
def b(user: str = Depends(identity)) -> str:
    return user
