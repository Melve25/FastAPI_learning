from fastapi import FastAPI, Request, status
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path

import fastapithird.models as models
from .database import engine
from .routers import auth, todos, admin, user

app = FastAPI()
models.Base.metadata.create_all(bind=engine)

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"

app.mount('/static', StaticFiles(directory=STATIC_DIR), name='static')


@app.get('/')
def test(request: Request):
	return RedirectResponse(url='/todo/todo-page', status_code=status.HTTP_302_FOUND)

@app.get('/healthy')
def health_check():
	return {'status': 'Healthy'}


app.include_router(auth.router)
app.include_router(todos.router)
app.include_router(admin.router)
app.include_router(user.router)


