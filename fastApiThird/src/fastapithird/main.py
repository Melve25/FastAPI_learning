from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from pathlib import Path

import fastapithird.models as models
from .database import engine
from .routers import auth, todos, admin, user

app = FastAPI()
models.Base.metadata.create_all(bind=engine)

BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "templates"

template = Jinja2Templates(directory=TEMPLATES_DIR)


@app.get('/')
def test(request: Request):
	return template.TemplateResponse('home.html', {'request': request})

@app.get('/healthy')
def health_check():
	return {'status': 'Healthy'}


app.include_router(auth.router)
app.include_router(todos.router)
app.include_router(admin.router)
app.include_router(user.router)


